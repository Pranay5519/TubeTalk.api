import os
import pkg_resources

# Read packages from requirements.txt
with open("requirements.txt", "r") as f:
    packages = [line.split("==")[0].strip() for line in f if line.strip()]

total_size = 0

for pkg_name in packages:
    try:
        dist = pkg_resources.get_distribution(pkg_name)
        package_path = dist.location
        folder_name = os.path.join(package_path, pkg_name)
        size = 0
        if os.path.exists(folder_name):
            for dirpath, dirnames, filenames in os.walk(folder_name):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    size += os.path.getsize(fp)
        print(f"{pkg_name}: {size/1024/1024:.2f} MB")
        total_size += size
    except pkg_resources.DistributionNotFound:
        print(f"{pkg_name}: Not installed")

print(f"\nTotal size of all listed packages: {total_size/1024/1024:.2f} MB")
