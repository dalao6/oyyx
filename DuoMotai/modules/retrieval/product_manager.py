import os
import json
from typing import Dict, Any, List


class ProductManager:
    def __init__(self, image_dir: str, spec_dir: str):
        """
        管理商品图片与规格信息
        :param image_dir: 图片目录，例如 data/product_images
        :param spec_dir: 商品规格 JSON 文件目录，例如 data/product_specs
        """
        self.image_dir = image_dir
        self.spec_dir = spec_dir
        self.products = {}  # { product_id: { image_path, price, description, tags } }

        self._load_all_products()

    def _load_all_products(self):
        """加载所有 JSON 商品规格并配对图片"""
        if not os.path.exists(self.spec_dir):
            print(f"[ProductManager] ⚠️ Spec directory not found: {self.spec_dir}")
            return

        for file_name in os.listdir(self.spec_dir):
            if file_name.endswith(".json"):
                spec_path = os.path.join(self.spec_dir, file_name)
                with open(spec_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for pid, info in data.items():
                    image_file = f"{pid}.jpg"
                    image_path = os.path.join(self.image_dir, image_file)
                    if not os.path.exists(image_path):
                        print(f"[ProductManager] ⚠️ Image not found for {pid}")
                        continue

                    self.products[pid] = {
                        "name": pid.replace("_", " ").title(),
                        "image": image_path,
                        "price": info.get("price", "未知价格"),
                        "description": info.get("description", "暂无描述"),
                        "tags": info.get("tags", []),  # 修复：原来是"tag"，应该是"tags"
                        # 添加尺码信息（如果存在）
                        "sizes": info.get("sizes", {})
                    }

        print(f"[ProductManager] ✅ Loaded {len(self.products)} products.")

    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """根据关键字搜索商品"""
        keyword = keyword.lower()
        results = []
        for pid, info in self.products.items():
            text = f"{info['name']} {info['description']} {' '.join(info['tags'])}".lower()
            if keyword in text:
                results.append(info)
        return results

    def search_product(self, product_name: str) -> Dict[str, Any]:
        """根据商品名称搜索商品"""
        # 尝试直接匹配
        if product_name in self.products:
            return self.products[product_name]
        
        # 尝试模糊匹配
        for pid, info in self.products.items():
            if product_name in pid or pid in product_name:
                return info
                
        # 使用关键词搜索
        results = self.search_by_keyword(product_name)
        if results:
            return results[0]  # 返回第一个匹配结果
            
        return None

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """通过商品ID获取商品信息"""
        return self.products.get(product_id, None)

    def get_product_with_size(self, product_id: str, size: str) -> Dict[str, Any]:
        """获取指定尺码的商品信息"""
        product = self.products.get(product_id, None)
        if not product:
            return None
            
        # 如果有尺码特定信息，则更新价格等
        if "sizes" in product and size in product["sizes"]:
            size_info = product["sizes"][size]
            updated_product = product.copy()
            updated_product["price"] = size_info.get("price", product["price"])
            updated_product["description"] = product["description"] + f" 尺码: {size}"
            return updated_product
            
        return product