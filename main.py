import os
import imagehash
from PIL import Image
from multiprocessing import Pool, cpu_count
import time

def get_image_hash(image_path):
    """获取图像的感知哈希值"""
    try:
        img = Image.open(image_path)
        return imagehash.phash(img)
    except Exception as e:
        print(f"无法处理图像 {image_path}: {e}")
        return None  # 返回 None，表示无法处理此文件

def process_image(image_path):
    """处理单个图片，返回哈希值和图片路径"""
    img_hash = get_image_hash(image_path)
    if img_hash is None:
        return None
    return (img_hash, image_path)

def find_images_in_directory(directory):
    """遍历目录并返回所有图片文件的路径"""
    image_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_paths.append(file_path)
    return image_paths

def find_duplicate_images(directory):
    """查找并返回重复图片"""
    hash_dict = {}  # 存储图片哈希值及其路径列表
    duplicates = []  # 存储重复图片路径和与之重复的图片路径

    # 获取所有子目录（避免直接处理C盘根目录）
    directories = [os.path.join(directory, sub_dir) for sub_dir in os.listdir(directory) if os.path.isdir(os.path.join(directory, sub_dir))]

    # 使用多进程遍历子文件夹
    with Pool(cpu_count()) as pool:
        all_image_paths = pool.map(find_images_in_directory, directories)

    # 合并所有目录的图片路径
    all_image_paths = [image_path for sublist in all_image_paths for image_path in sublist]

    # 使用多进程处理图片哈希计算
    with Pool(cpu_count()) as pool:
        results = pool.map(process_image, all_image_paths)

    # 处理结果，检查重复
    for img_hash, file_path in filter(None, results):
        if img_hash in hash_dict:
            # 如果哈希值已存在，则为重复图片，记录与之前图片的重复信息
            duplicates.append((file_path, hash_dict[img_hash]))  # 记录重复图片和原图片的路径
            print(f"发现重复图片: {file_path} 与 {hash_dict[img_hash]}")
        else:
            # 如果哈希值不存在，则添加到哈希字典中
            hash_dict[img_hash] = file_path

    return duplicates

def delete_duplicates(duplicates):
    """删除重复的图片"""
    for duplicate, original in duplicates:
        try:
            os.remove(duplicate)
            print(f"已删除重复图片: {duplicate} (原图片: {original})")
        except Exception as e:
            print(f"删除失败 {duplicate}: {e}")

def main():
    directory = input("请输入图片文件夹路径 (例如: C:/): ")

    # 转换路径中的反斜杠为正斜杠
    directory = directory.replace("\\", "/")

    start_time = time.time()

    if not os.path.exists(directory):
        print("文件夹路径无效")
        return

    print("正在查找重复图片...")
    duplicates = find_duplicate_images(directory)

    if duplicates:
        print("\n发现的重复图片:")
        for duplicate, original in duplicates:
            print(f"重复图片: {duplicate} 与原图片: {original}")
        print(f'一共用时{(time.time()-start_time):.2f} S')    
        delete_choice = input(f"\n是否删除这些重复图片,共计{len(duplicates)}张图片? (y/n): ").lower()
        if delete_choice == 'y':
            delete_duplicates(duplicates)
        else:
            print("未删除任何图片")
    else:
        print("没有发现重复图片")

if __name__ == "__main__":
    main()
