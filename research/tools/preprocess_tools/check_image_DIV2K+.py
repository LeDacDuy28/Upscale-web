import os
import glob
from PIL import Image
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


def analyze_resolutions(root_dir):
    # Các thư mục cần phân tích
    dirs = {
        "DIV2K_train": ["DIV2K_HR", "DIV2K_LR"],
        "DIV2K_valid": ["DIV2K_valid_HR", "DIV2K_valid_LR"],
        "OutdoorSceneTest300": ["OutdoorSceneTest300_HR", "OutdoorSceneTest300_LR"],
        "Flickr2K": ["Flickr2K_HR", "Flickr2K_LR"],
        "OST": ["OST_HR", "OST_LR"]
    }

    results = {}

    # Đối với mỗi tập dữ liệu
    for dataset, folders in dirs.items():
        results[dataset] = {}

        # Đối với mỗi loại ảnh (HR/LR)
        for folder in folders:
            # Xác định loại ảnh
            img_type = "HR" if "_HR" in folder else "LR"

            # Tìm đường dẫn đến thư mục
            folder_path = find_folder(root_dir, folder)
            if not folder_path:
                print(f"Không tìm thấy thư mục: {folder}")
                continue

            print(f"Đang phân tích {folder} tại {folder_path}...")

            # Tìm tất cả các file ảnh
            image_files = []
            for ext in ["*.jpg", "*.png", "*.bmp", "*.jpeg", "*.tif", "*.tiff"]:
                image_files.extend(glob.glob(os.path.join(folder_path, "**", ext), recursive=True))

            if not image_files:
                print(f"Không tìm thấy ảnh trong thư mục: {folder}")
                continue

            # Phân tích độ phân giải
            resolutions = []
            areas = []  # Lưu trữ diện tích pixel (width*height)
            for img_path in image_files:
                try:
                    with Image.open(img_path) as img:
                        width, height = img.size
                        resolutions.append((width, height))
                        areas.append(width * height)
                except Exception as e:
                    print(f"Lỗi khi mở ảnh {img_path}: {e}")

            # Tính toán thống kê
            if not resolutions:
                continue

            results[dataset][img_type] = {
                "total_images": len(resolutions),
                "min_resolution": min(resolutions, key=lambda x: x[0] * x[1]),
                "max_resolution": max(resolutions, key=lambda x: x[0] * x[1]),
                "most_common": Counter(resolutions).most_common(1)[0],
                "all_resolutions": Counter(resolutions),
                "pixel_areas": areas
            }

    return results


def find_folder(root_dir, target_folder):
    """Tìm đường dẫn đến thư mục cần tìm"""
    for root, dirs, _ in os.walk(root_dir):
        if target_folder in dirs:
            return os.path.join(root, target_folder)
    return None


def format_resolution(res):
    """Format độ phân giải để in ra dạng đẹp hơn"""
    return f"{res[0]}×{res[1]}"


def print_results(results):
    """In kết quả phân tích"""
    for dataset, data in results.items():
        print(f"\n{'=' * 50}")
        print(f"KẾT QUẢ CHO {dataset}")
        print(f"{'=' * 50}")

        for img_type, stats in data.items():
            print(f"\n{'*' * 40}")
            print(f"* {img_type} ({stats['total_images']} ảnh)")
            print(f"{'*' * 40}")

            min_res = stats['min_resolution']
            max_res = stats['max_resolution']
            most_common = stats['most_common']

            print(f"Độ phân giải nhỏ nhất: {format_resolution(min_res)} ({min_res[0] * min_res[1]:,} pixels)")
            print(f"Độ phân giải lớn nhất: {format_resolution(max_res)} ({max_res[0] * max_res[1]:,} pixels)")
            print(f"Độ phân giải phổ biến nhất: {format_resolution(most_common[0])} ({most_common[1]} ảnh)")

            # Top 10 độ phân giải phổ biến
            print("\nTop 10 độ phân giải phổ biến:")
            print("-" * 40)
            print(f"{'Độ phân giải':<20} | {'Pixels':<15} | {'Số lượng':<10}")
            print("-" * 40)
            for res, count in stats['all_resolutions'].most_common(10):
                print(f"{format_resolution(res):<20} | {res[0] * res[1]:,} | {count:<10}")


def plot_improved_histograms(results, output_dir="resolution_charts_DIV2K"):
    """Vẽ biểu đồ histogram cải tiến cho phân bố độ phân giải"""
    # Tạo thư mục đầu ra nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)

    for dataset, data in results.items():
        for img_type, stats in data.items():
            # 1. Biểu đồ dạng histogram cho diện tích pixel
            plt.figure(figsize=(14, 8))

            areas = stats['pixel_areas']
            # Xác định số bins phù hợp với dữ liệu
            if len(set(areas)) > 50:
                bins = min(50, len(set(areas)))
            else:
                bins = len(set(areas))

            plt.hist(areas, bins=bins, color='skyblue', edgecolor='black')

            plt.title(f'Pixel area distribution - {dataset} {img_type}', fontsize=16)
            plt.xlabel('Area (pixels)', fontsize=14)
            plt.ylabel('Number of Images', fontsize=14)
            plt.ticklabel_format(style='plain', axis='x')
            plt.xticks(fontsize=12, rotation=45)
            plt.yticks(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'{dataset}_{img_type}_area_histogram.png'), dpi=300)
            plt.close()

            # 2. Biểu đồ phân bố theo chiều rộng và chiều cao
            plt.figure(figsize=(16, 10))

            widths = [res[0] for res in stats['all_resolutions'].keys()]
            heights = [res[1] for res in stats['all_resolutions'].keys()]
            counts = list(stats['all_resolutions'].values())

            # Tạo scatter plot với kích thước điểm tương ứng với số lượng
            sizes = [count * 20 for count in counts]  # Điều chỉnh kích thước điểm

            plt.scatter(widths, heights, s=sizes, alpha=0.7, edgecolor='black')

            # Thêm nhãn cho các điểm phổ biến nhất
            for i, ((w, h), count) in enumerate(
                    sorted(stats['all_resolutions'].items(), key=lambda x: x[1], reverse=True)[:5]):
                plt.annotate(f"{w}×{h}\n({count} ảnh)", (w, h),
                             xytext=(10, 10), textcoords='offset points',
                             fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7))

            plt.title(f'Pixel area distribution - {dataset} {img_type}', fontsize=16)
            plt.xlabel('Width (pixels)', fontsize=14)
            plt.ylabel('Height (pixels)', fontsize=14)
            plt.ticklabel_format(style='plain')
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'{dataset}_{img_type}_resolution_scatter.png'), dpi=300)
            plt.close()

            # 3. Hiển thị top N độ phân giải phổ biến nhất
            plt.figure(figsize=(16, 12))

            top_n = min(15, len(stats['all_resolutions']))
            top_resolutions = stats['all_resolutions'].most_common(top_n)

            resolution_labels = [f"{w}×{h}\n({w * h:,}px)" for (w, h), _ in top_resolutions]
            counts = [count for _, count in top_resolutions]

            plt.bar(range(len(counts)), counts, color='lightblue', edgecolor='black')
            plt.xticks(range(len(counts)), resolution_labels, rotation=45, ha='right', fontsize=12)
            plt.yticks(fontsize=12)

            plt.title(f'Top {top_n} common resolution - {dataset} {img_type}', fontsize=16)
            plt.xlabel('Resolution', fontsize=14)
            plt.ylabel('Number of images', fontsize=14)
            plt.grid(axis='y', alpha=0.3)

            # Thêm giá trị số lượng trên mỗi cột
            for i, count in enumerate(counts):
                plt.text(i, count + 0.5, str(count), ha='center', fontsize=10)

            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'{dataset}_{img_type}_top_resolutions.png'), dpi=300)
            plt.close()


# Hàm tạo báo cáo tổng hợp
def generate_summary_report(results, output_file="resolution_analysis_summary_DIV2K+.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("BÁO CÁO PHÂN TÍCH ĐỘ PHÂN GIẢI ẢNH\n")
        f.write("=" * 50 + "\n\n")

        # Tổng hợp số lượng ảnh
        f.write("TỔNG HỢP SỐ LƯỢNG ẢNH\n")
        f.write("-" * 50 + "\n")

        total_hr = 0
        total_lr = 0

        for dataset, data in results.items():
            hr_count = data.get("HR", {}).get("total_images", 0)
            lr_count = data.get("LR", {}).get("total_images", 0)
            total_hr += hr_count
            total_lr += lr_count

            f.write(f"{dataset:25} - HR: {hr_count:5} ảnh, LR: {lr_count:5} ảnh\n")

        f.write("-" * 50 + "\n")
        f.write(f"{'TỔNG CỘNG':25} - HR: {total_hr:5} ảnh, LR: {total_lr:5} ảnh\n\n")

        # Chi tiết từng dataset
        for dataset, data in results.items():
            f.write(f"\n{dataset.upper()}\n")
            f.write("=" * 50 + "\n")

            for img_type, stats in data.items():
                f.write(f"\n{img_type} ({stats['total_images']} ảnh)\n")
                f.write("-" * 40 + "\n")

                min_res = stats['min_resolution']
                max_res = stats['max_resolution']
                most_common = stats['most_common']

                f.write(f"Độ phân giải nhỏ nhất: {format_resolution(min_res)} ({min_res[0] * min_res[1]:,} pixels)\n")
                f.write(f"Độ phân giải lớn nhất: {format_resolution(max_res)} ({max_res[0] * max_res[1]:,} pixels)\n")
                f.write(f"Độ phân giải phổ biến nhất: {format_resolution(most_common[0])} ({most_common[1]} ảnh)\n\n")

                # Top 5 độ phân giải phổ biến
                f.write("Top 5 độ phân giải phổ biến:\n")
                for i, (res, count) in enumerate(stats['all_resolutions'].most_common(5), 1):
                    f.write(f"{i}. {format_resolution(res):15} - {count:4} ảnh ({res[0] * res[1]:,} pixels)\n")
                f.write("\n")

def summarize_and_plot_global(results, output_dir="resolution_charts_DIV2K"):
    all_resolutions = []
    all_areas = []
    aspect_ratios = []

    resolution_counter = Counter()

    for dataset in results.values():
        for stats in dataset.values():
            for (w, h), count in stats["all_resolutions"].items():
                all_resolutions.extend([(w, h)] * count)
                all_areas.extend([w * h] * count)
                resolution_counter[f"{w}×{h}"] += count
                if h != 0:
                    ratio = round(w / h, 2)
                    aspect_ratios.extend([ratio] * count)

    total_images = len(all_resolutions)
    unique_resolutions = len(set(all_resolutions))
    min_res = min(all_resolutions, key=lambda x: x[0] * x[1])
    max_res = max(all_resolutions, key=lambda x: x[0] * x[1])
    ratio_counter = Counter(aspect_ratios)

    print("\n📊 TỔNG HỢP TOÀN BỘ DỮ LIỆU 📊")
    print(f"Tổng số ảnh: {total_images}")
    print(f"Số độ phân giải khác nhau: {unique_resolutions}")
    print(f"Độ phân giải nhỏ nhất: {min_res[0]}×{min_res[1]}")
    print(f"Độ phân giải lớn nhất: {max_res[0]}×{max_res[1]}")

    print("\n📐 Top 10 TỶ LỆ KHUNG HÌNH phổ biến:")
    for ratio, count in ratio_counter.most_common(10):
        print(f"Tỷ lệ {ratio:.2f}: {count} ảnh")

    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(14, 6))

    # Chỉ lấy top 15 độ phân giải phổ biến
    top_resolutions = resolution_counter.most_common(15)
    labels = [label for label, _ in top_resolutions]
    values = [count for _, count in top_resolutions]

    plt.bar(labels, values, color='skyblue', edgecolor='black')
    plt.title("Top 15 Global Resolutions (W×H)")
    plt.xlabel("Resolution (W×H)")
    plt.ylabel("Number of Images")
    plt.xticks(rotation=45, fontsize=9)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "global_pixel_area_histogram.png"))
    plt.close()

    plt.figure(figsize=(10, 5))
    top_ratios = ratio_counter.most_common(15)
    labels = [str(r[0]) for r in top_ratios]
    values = [r[1] for r in top_ratios]
    plt.bar(labels, values, color='lightcoral', edgecolor='black')
    plt.title("Top 15 Aspect Ratios (W/H)")
    plt.xlabel("Aspect Ratio")
    plt.ylabel("Number of Images")
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "global_aspect_ratio_histogram.png"))
    plt.close()




# Sử dụng hàm
if __name__ == "__main__":
    root_dir = "D:\\EnhanceVideo_ImageDLM\\data\\DIV2K+degra"  # Thay đổi đường dẫn này tới thư mục gốc
    results = analyze_resolutions(root_dir)

    # In kết quả ra màn hình
    print_results(results)

    # Tạo biểu đồ cải tiến
    plot_improved_histograms(results)

    # Sử dụng trong main
    summarize_and_plot_global(results)

    # Tạo báo cáo tổng hợp
    generate_summary_report(results)

    print("\nĐã hoàn thành phân tích. Các biểu đồ được lưu trong thư mục 'resolution_charts_DIV2K+'")
    print("Báo cáo tổng hợp được lưu trong file 'resolution_analysis_summary_DIV2K+.txt'")