import requests
import time
import logging
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
CONFIG = {
    'base_url': "http://localhost:5000",
    'core_servers': ["Server1", "Server2", "Server3"],  
    'results_file': "analysis/results/scalability.txt",
    'request_count': 10000,
    'concurrency': 20,
    'timeout': 15,
    'stabilization_delay': 5,
    'max_retries': 3,
    'retry_delay': 2
}

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis/results/scalability_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('scalability_test')


def make_request(url):
    try:
        resp = requests.get(url, timeout=CONFIG['timeout'])
        if resp.status_code == 200:
            message = resp.json().get("message", "")
            server = message.split(":")[1].strip() if ":" in message else "unknown"
            return True, server
        return False, f"http_{resp.status_code}"
    except Exception as e:
        return False, str(e)


def reset_servers():
    """Reset to core server configuration"""
    for attempt in range(CONFIG['max_retries']):
        try:
            # Get current state
            resp = requests.get(f"{CONFIG['base_url']}/rep", timeout=CONFIG['timeout'])
            current_replicas = resp.json()["message"]["replicas"]

            # Remove non-core servers
            to_remove = [r for r in current_replicas if r not in CONFIG['core_servers']]
            for server in to_remove:
                try:
                    requests.delete(
                        f"{CONFIG['base_url']}/rm",
                        json={"n": 1, "hostnames": [server]},
                        timeout=CONFIG['timeout']
                    )
                    time.sleep(1)
                except:
                    continue

            # Verify reset
            time.sleep(CONFIG['stabilization_delay'])
            resp = requests.get(f"{CONFIG['base_url']}/rep", timeout=CONFIG['timeout'])
            replicas = resp.json()["message"]["replicas"]
            logger.info(f"Current replicas after removal: {replicas}")
            logger.info(f"Expected core servers: {CONFIG['core_servers']}")
            if set(replicas) == set(CONFIG['core_servers']):
                return True

        except Exception as e:
            logger.warning(f"Reset attempt {attempt+1} failed: {str(e)}")
            time.sleep(CONFIG['retry_delay'])

    logger.error("Failed to reset servers")
    return False


def scale_to_target(target_n):
    """Scale to target number of servers"""
    for attempt in range(CONFIG['max_retries']):
        try:
            resp = requests.get(f"{CONFIG['base_url']}/rep", timeout=CONFIG['timeout'])
            current_n = resp.json()["message"]["N"]
            delta = target_n - current_n

            if delta > 0:
                requests.post(
                    f"{CONFIG['base_url']}/add",
                    json={"n": delta, "hostnames": []},
                    timeout=CONFIG['timeout']
                )
            elif delta < 0:
                requests.delete(
                    f"{CONFIG['base_url']}/rm",
                    json={"n": abs(delta), "hostnames": []},
                    timeout=CONFIG['timeout']
                )

            time.sleep(CONFIG['stabilization_delay'])
            resp = requests.get(f"{CONFIG['base_url']}/rep", timeout=CONFIG['timeout'])
            if resp.json()["message"]["N"] == target_n:
                logger.info(f"Successfully scaled to {target_n} servers")
                return True

        except Exception as e:
            logger.warning(f"Scale attempt {attempt+1} failed: {str(e)}")
            time.sleep(CONFIG['retry_delay'])

    logger.error(f"Failed to scale to {target_n} servers")
    return False


def run_load_test():
    """Run concurrent load test"""
    counts = defaultdict(int)
    errors = defaultdict(int)
    success = 0

    with ThreadPoolExecutor(max_workers=CONFIG['concurrency']) as executor:
        futures = [
            executor.submit(
                make_request,
                f"{CONFIG['base_url']}/home"
            )
            for _ in range(CONFIG['request_count'])
        ]

        for i, future in enumerate(as_completed(futures)):
            ok, result = future.result()
            if ok:
                counts[result] += 1
                success += 1
            else:
                errors[result] += 1

            if (i + 1) % 1000 == 0:
                logger.info(f"Completed {i + 1}/{CONFIG['request_count']} requests")

    return counts, errors, success


def run_scalability_test():
    """Main test execution"""
    try:
        if not reset_servers():
            raise RuntimeError("Initial reset failed")

        results = []

        for target_n in range(2, 7):
            logger.info(f"\n=== Testing N={target_n} servers ===")

            if not scale_to_target(target_n):
                logger.error(f"Skipping N={target_n} due to scaling failure")
                continue

            counts, errors, success = run_load_test()

            if success > 0:
                distribution = {k: v / success for k, v in counts.items()}
                avg_load = success / target_n
            else:
                distribution = {}
                avg_load = 0

            error_rate = sum(errors.values()) / CONFIG['request_count']

            logger.info(f"Results for N={target_n}:")
            logger.info(f"• Successful requests: {success}/{CONFIG['request_count']}")
            logger.info(f"• Error rate: {error_rate:.1%}")
            logger.info(f"• Average load: {avg_load:.1f} req/server")
            logger.info("• Distribution:")
            for server, percent in distribution.items():
                logger.info(f"  - {server}: {percent:.1%}")

            results.append((target_n, avg_load))

        os.makedirs(os.path.dirname(CONFIG['results_file']), exist_ok=True)
        with open(CONFIG['results_file'], 'w') as f:
            for n, load in results:
                f.write(f"{n} {load:.1f}\n")

        logger.info(f"\nTest complete. Results saved to {CONFIG['results_file']}")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == '__main__':
    run_scalability_test()
