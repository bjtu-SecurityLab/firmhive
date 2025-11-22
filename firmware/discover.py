import os
import argparse

# Default dataset root (anonymized). Can be overridden by env KARONTE_DATASET_DIR
# or via the --base_dir argument.
BASE_FIRMWARE_DIR = os.environ.get("KARONTE_DATASET_DIR", "/path/to/karonte_dataset")

BRANDS_IN_ORDER = ["d-link", "NETGEAR", "Tenda", "TP_Link"]

def discover_firmware_targets(base_dir, brands_in_order):

    targets = []
    for brand in brands_in_order:
        brand_path = os.path.join(base_dir, brand, "analyzed")
        if not os.path.isdir(brand_path):
            continue
        
        for item in sorted(os.listdir(brand_path)):
            full_path = os.path.join(brand_path, item)
            if os.path.isdir(full_path) and item != "results":
                targets.append(full_path)
    return targets

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover firmware directories for analysis.")
    parser.add_argument("--base_dir", type=str, default=BASE_FIRMWARE_DIR, 
                        help=f"The base directory to search for firmware brands. Defaults to '{BASE_FIRMWARE_DIR}'.")
    args = parser.parse_args()

    firmware_list = discover_firmware_targets(args.base_dir, BRANDS_IN_ORDER)
    print(f"Found {len(firmware_list)} firmware targets")
    for target in firmware_list:
        print(target) 
