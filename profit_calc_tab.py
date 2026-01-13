import json
import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QFormLayout, QGroupBox,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)


class ProfitCalcTab(QWidget):
    def __init__(self):
        super().__init__()
        self.recipes_data = self.parse_config()
        self.material_prices_cache = {}  # 缓存材料单价，实现配方间共享
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.init_profit_tab()
        self.load_config() # 加载历史配置

    def parse_config(self):
        recipes = {}
        current_section = None
        try:
            with open("config.ini", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("[") and line.endswith("]"):
                        current_section = line.lstrip("[").rstrip("]").strip()
                        if current_section not in recipes:
                            recipes[current_section] = []
                        continue
                    if not line or line.startswith(";"):
                        continue
                    if current_section and line.startswith("#"):
                        parts = [p.strip() for p in line.split("#") if p.strip()]
                        if len(parts) < 4: continue
                        recipe_name = parts[1]
                        try:
                            single_energy_cost = float(parts[2])
                        except ValueError:
                            single_energy_cost = 0.0
                        materials = {}
                        for i in range(3, len(parts), 2):
                            mat_name = parts[i]
                            if i + 1 >= len(parts): break
                            try:
                                mat_num = int(parts[i+1])
                            except ValueError:
                                mat_num = 0
                            if mat_name: materials[mat_name] = mat_num
                        recipes[current_section].append({
                            "name": recipe_name,
                            "single_energy_cost": single_energy_cost,
                            "materials": materials
                        })
        except FileNotFoundError:
            print("错误：未找到 config.ini 文件")
        except Exception as e:
            print(f"解析配置文件出错：{str(e)}")
        return recipes

    def init_profit_tab(self):
        top_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItems(list(self.recipes_data.keys()))
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        top_layout.addWidget(QLabel("选择类别:"))
        top_layout.addWidget(self.category_combo)
        top_layout.addSpacing(20)
        
        self.recipe_combo = QComboBox()
        self.recipe_combo.currentIndexChanged.connect(self.on_recipe_changed)
        top_layout.addWidget(QLabel("选择配方:"))
        top_layout.addWidget(self.recipe_combo)
        top_layout.addStretch()
        self.main_layout.addLayout(top_layout)
        
        self.material_table = QTableWidget()
        self.material_table.setColumnCount(4)
        self.material_table.setHorizontalHeaderLabels(["材料名称", "所需数量", "单价(成本)", "小计(单个成本)"])
        self.material_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.material_table)
        
        calc_group = QGroupBox("利润计算")
        calc_layout = QFormLayout()
        
        self.single_price_input = QLineEdit("0.00")
        calc_layout.addRow("单个成品售价:", self.single_price_input)
        
        self.single_energy_label = QLabel("0.00")
        calc_layout.addRow("单个精力成本:", self.single_energy_label)
        
        self.total_energy_label = QLabel("0.00")
        calc_layout.addRow("总共需要精力:", self.total_energy_label)
        
        self.quantity_input = QLineEdit("1")
        calc_layout.addRow("制作数量:", self.quantity_input)
        
        self.total_cost_label = QLabel("0.00")
        calc_layout.addRow("总成本:", self.total_cost_label)
        
        self.total_profit_label = QLabel("0.00")
        calc_layout.addRow("总利润:", self.total_profit_label)
        
        self.calc_btn = QPushButton("计算利润")
        self.calc_btn.clicked.connect(self.calculate_profit)
        calc_layout.addRow(self.calc_btn)
        
        calc_group.setLayout(calc_layout)
        self.main_layout.addWidget(calc_group)
        
        if self.recipes_data:
            self.on_category_changed(0)

    def on_category_changed(self, index):
        category = self.category_combo.currentText()
        self.recipe_combo.clear()
        if category in self.recipes_data:
            for recipe in self.recipes_data[category]:
                self.recipe_combo.addItem(recipe["name"])

    def on_recipe_changed(self, index):
        category = self.category_combo.currentText()
        recipe_name = self.recipe_combo.currentText()
        if not recipe_name: return
        
        selected_recipe = None
        for recipe in self.recipes_data.get(category, []):
            if recipe["name"] == recipe_name:
                selected_recipe = recipe
                break
        
        if selected_recipe:
            self.single_energy_label.setText(f"{selected_recipe['single_energy_cost']:.2f}")
            materials = selected_recipe["materials"]
            self.material_table.setRowCount(len(materials))
            for row, (mat_name, mat_num) in enumerate(materials.items()):
                name_item = QTableWidgetItem(mat_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.material_table.setItem(row, 0, name_item)
                
                num_item = QTableWidgetItem(str(mat_num))
                num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
                self.material_table.setItem(row, 1, num_item)
                
                # 自动填充缓存的价格
                saved_price = self.material_prices_cache.get(mat_name, "0.00")
                price_item = QTableWidgetItem(str(saved_price))
                self.material_table.setItem(row, 2, price_item)
                
                subtotal_item = QTableWidgetItem("0.00")
                subtotal_item.setFlags(subtotal_item.flags() & ~Qt.ItemIsEditable)
                self.material_table.setItem(row, 3, subtotal_item)

    def calculate_profit(self):
        try:
            quantity = int(self.quantity_input.text())
            quantity = max(quantity, 1)
        except ValueError:
            quantity = 1
        
        single_material_cost = 0.0
        for row in range(self.material_table.rowCount()):
            mat_name = self.material_table.item(row, 0).text()
            mat_num = int(self.material_table.item(row, 1).text())
            try:
                mat_price_text = self.material_table.item(row, 2).text()
                mat_price = float(mat_price_text)
                # 更新缓存
                self.material_prices_cache[mat_name] = mat_price_text
            except ValueError:
                mat_price = 0.0
            
            mat_subtotal = mat_price * mat_num
            self.material_table.setItem(row, 3, QTableWidgetItem(f"{mat_subtotal:.2f}"))
            single_material_cost += mat_subtotal
        
        try:
            single_energy_cost = float(self.single_energy_label.text())
        except ValueError:
            single_energy_cost = 0.0
        
        try:
            single_sell_price = float(self.single_price_input.text())
        except ValueError:
            single_sell_price = 0.0

        total_energy = quantity * single_energy_cost
        self.total_energy_label.setText(f"{total_energy:.2f}")
        
        total_material_cost = single_material_cost * quantity
        total_energy_cost = single_energy_cost * quantity
        total_cost = total_material_cost + total_energy_cost
        
        total_sell_price = single_sell_price * quantity
        total_profit = total_sell_price - total_cost
        
        self.total_cost_label.setText(f"{total_cost:.2f}")
        self.total_profit_label.setText(f"{total_profit:.2f}")

    # ========== 新增：配置保存/加载 ==========
    def save_config(self):
        """保存利润计算相关的配置"""
        # 在保存前运行一次计算，以确保缓存了最新的单价
        self.calculate_profit()
        
        config_data = {
            "profit_calc": {
                "sell_price": self.single_price_input.text(),
                "quantity": self.quantity_input.text(),
                "material_prices": self.material_prices_cache
            }
        }
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    all_config = json.load(f)
                all_config.update(config_data)
            else:
                all_config = config_data
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(all_config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存利润配置失败：{e}")

    def load_config(self):
        """加载历史利润计算配置"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        if not os.path.exists(config_path): return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                all_config = json.load(f)
            profit_config = all_config.get("profit_calc", {})
            if not profit_config: return

            self.single_price_input.setText(profit_config.get("sell_price", "0.00"))
            self.quantity_input.setText(profit_config.get("quantity", "1"))
            self.material_prices_cache = profit_config.get("material_prices", {})
            
            # 刷新一次当前表格显示
            self.on_recipe_changed(0)
        except Exception as e:
            print(f"加载利润配置失败：{e}")