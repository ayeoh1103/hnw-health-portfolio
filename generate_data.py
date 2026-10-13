# -*- coding: utf-8 -*-
"""
高净值人群健康画像数据集 —— 作品集数据底座
================================================
用途：依据数据产品「高净值人群健康画像数据集」（覆盖 340+ 城市、中高端体检人群）
      所公开的人群特征与指标维度，构建一份可复现的**模拟演示数据集**与分层统计结果，
      用于数据分析作品集的可视化呈现。

重要：本脚本产出的是**模拟数据（synthetic data）**，非数据交易所的真实成交数据。
      真实数据集为付费产品，需通过 marketplace.selectdataset.com 购买后获取。
      模拟参数参考公开流行病学资料（中国居民营养与慢性病状况报告、中国心血管健康
      与疾病报告、中国成人血脂异常防治指南等）进行校准，用于方法演示与可视化表达。

输出：
  hnw_health_dataset_simulated.csv   个体级模拟数据（5,000 条，已匿名化）
  dashboard_data.json                分层聚合统计结果（供前端图表消费）
"""

import csv
import json
import math
import os
import random

random.seed(20261013)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
N = 5000

# ----------------------------------------------------------------------------
# 1. 人群结构设定
# ----------------------------------------------------------------------------
AGE_GROUPS = ["25-35岁", "36-45岁", "46-55岁", "56岁以上"]
AGE_P = [0.35, 0.35, 0.20, 0.10]
AGE_MID = {"25-35岁": 30, "36-45岁": 40, "46-55岁": 50, "56岁以上": 62}

GENDERS = ["男", "女"]
GENDER_P = [0.52, 0.48]

TIERS = ["一线城市", "新一线城市", "二线城市", "三四线城市"]
TIER_P = [0.25, 0.30, 0.25, 0.20]
TIER_NUM = {"一线城市": 0, "新一线城市": 1, "二线城市": 2, "三四线城市": 3}

OCCUPS = ["城市白领", "企业管理层", "高收入自由职业者", "其他专业人群"]
OCCUP_P = [0.45, 0.30, 0.15, 0.10]

PAYS = ["个人自费", "企业团检", "家庭套餐"]
PAY_P = [0.33, 0.45, 0.22]          # 个人付费体检占比约三分之一（数据集公开信息）

LABELS = ["主动筛查型", "基础保障型", "被动履约型"]

# 城市池：340 个城市（与数据集「覆盖全国 340+ 城市」口径对齐）
# 线级划分参照主流城市商业魅力/消费力分层：一线 4、新一线 15、二线 92、三四线 229
CITIES = {
    "一线城市": ["上海", "北京", "深圳", "广州"],
    "新一线城市": ["成都", "杭州", "重庆", "苏州", "武汉", "西安", "南京", "长沙",
                   "天津", "郑州", "东莞", "青岛", "昆明", "宁波", "合肥"],
    "二线城市": [
        "无锡", "厦门", "济南", "福州", "大连", "沈阳", "哈尔滨", "长春", "石家庄",
        "南宁", "贵阳", "太原", "南昌", "兰州", "海口", "常州", "南通", "徐州",
        "温州", "佛山", "珠海", "中山", "惠州", "泉州", "绍兴", "嘉兴", "台州",
        "金华", "扬州", "盐城", "泰州", "镇江", "淮安", "连云港", "烟台", "潍坊",
        "淄博", "济宁", "临沂", "威海", "洛阳", "开封", "新乡", "南阳", "襄阳",
        "宜昌", "荆州", "十堰", "孝感", "株洲", "湘潭", "衡阳", "岳阳", "常德",
        "郴州", "赣州", "九江", "上饶", "芜湖", "蚌埠", "阜阳", "安庆", "马鞍山",
        "绵阳", "宜宾", "南充", "泸州", "遵义", "桂林", "柳州", "湛江", "汕头",
        "江门", "茂名", "肇庆", "三亚", "拉萨", "呼和浩特", "包头", "银川",
        "西宁", "乌鲁木齐", "克拉玛依", "大庆", "鞍山", "吉林", "大同", "榆林",
        "泰安", "德州", "聊城", "菏泽", "枣庄", "日照",
    ],
    "三四线城市": [
        "唐山", "秦皇岛", "邯郸", "邢台", "保定", "张家口", "承德", "沧州", "廊坊", "衡水",
        "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "忻州", "临汾", "吕梁",
        "乌海", "赤峰", "通辽", "鄂尔多斯", "呼伦贝尔", "巴彦淖尔", "乌兰察布",
        "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛",
        "四平", "辽源", "通化", "白山", "松原", "白城",
        "齐齐哈尔", "鸡西", "鹤岗", "双鸭山", "伊春", "佳木斯", "七台河", "牡丹江", "黑河", "绥化",
        "宿迁", "湖州", "衢州", "舟山", "丽水",
        "淮南", "淮北", "铜陵", "黄山", "宿州", "滁州", "六安", "亳州", "池州", "宣城",
        "莆田", "三明", "漳州", "南平", "龙岩", "宁德",
        "景德镇", "萍乡", "新余", "鹰潭", "吉安", "宜春", "抚州",
        "东营", "滨州", "平顶山", "安阳", "鹤壁", "焦作", "濮阳", "许昌", "漯河",
        "三门峡", "商丘", "信阳", "周口", "驻马店", "济源",
        "黄石", "鄂州", "荆门", "黄冈", "咸宁", "随州", "仙桃", "潜江", "天门",
        "邵阳", "张家界", "益阳", "永州", "怀化", "娄底",
        "韶关", "梅州", "汕尾", "河源", "阳江", "清远", "潮州", "揭阳", "云浮",
        "梧州", "北海", "防城港", "钦州", "贵港", "玉林", "百色", "贺州", "河池", "来宾", "崇左",
        "三沙", "儋州",
        "自贡", "攀枝花", "德阳", "广元", "遂宁", "内江", "乐山", "眉山", "广安",
        "达州", "雅安", "巴中", "资阳",
        "六盘水", "安顺", "毕节", "铜仁",
        "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧",
        "日喀则", "昌都", "林芝", "山南", "那曲",
        "铜川", "宝鸡", "咸阳", "渭南", "延安", "汉中", "安康", "商洛",
        "嘉峪关", "金昌", "白银", "天水", "武威", "张掖", "平凉", "酒泉", "庆阳", "定西", "陇南",
        "海东", "石嘴山", "吴忠", "固原", "中卫",
        "吐鲁番", "哈密", "昌吉", "博尔塔拉", "巴音郭楞", "阿克苏", "克孜勒苏", "喀什",
        "伊犁", "塔城", "阿勒泰", "石河子", "阿拉尔", "图木舒克", "五家渠",
        "昆山", "江阴", "张家港", "常熟", "太仓", "宜兴", "义乌", "慈溪", "余姚",
        "诸暨", "上虞", "晋江", "石狮", "南安", "惠安", "龙口", "莱州", "寿光",
        "诸城", "滕州", "新泰", "荣成", "满洲里", "二连浩特", "珲春", "绥芬河",
    ],
}
CITY_POOL_SIZE = sum(len(v) for v in CITIES.values())


def g(mu, sd):
    return random.gauss(mu, sd)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def prob(base, *effs):
    return clamp(base + sum(effs), 0.01, 0.96)


def pick(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def pct(values, q):
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * q
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


# ----------------------------------------------------------------------------
# 2. 加项（增值检查项目）设定
# ----------------------------------------------------------------------------
ADDON_ITEMS = [
    ("肿瘤标志物筛查", {"主动筛查型": 0.72, "基础保障型": 0.40, "被动履约型": 0.16}),
    ("低剂量胸部CT", {"主动筛查型": 0.60, "基础保障型": 0.28, "被动履约型": 0.11}),
    ("超声升级(甲状腺/乳腺/颈动脉)", {"主动筛查型": 0.66, "基础保障型": 0.38, "被动履约型": 0.15}),
    ("无痛胃肠镜", {"主动筛查型": 0.44, "基础保障型": 0.19, "被动履约型": 0.06}),
    ("冠脉CTA/心脑血管深度筛查", {"主动筛查型": 0.36, "基础保障型": 0.15, "被动履约型": 0.04}),
    ("易感基因/遗传风险检测", {"主动筛查型": 0.30, "基础保障型": 0.09, "被动履约型": 0.03}),
    ("骨密度检测", {"主动筛查型": 0.28, "基础保障型": 0.13, "被动履约型": 0.05}),
    ("妇科专项(HPV/TCT)", {"主动筛查型": 0.30, "基础保障型": 0.13, "被动履约型": 0.05}),
    ("免疫与微量元素评估", {"主动筛查型": 0.25, "基础保障型": 0.11, "被动履约型": 0.04}),
    ("营养代谢/肠道菌群评估", {"主动筛查型": 0.23, "基础保障型": 0.08, "被动履约型": 0.03}),
]

# 行为标签随城市线级、年龄段的倾向性权重
TIER_MULT = {
    "主动筛查型": {"一线城市": 1.30, "新一线城市": 1.12, "二线城市": 0.92, "三四线城市": 0.72},
    "基础保障型": {"一线城市": 1.00, "新一线城市": 1.02, "二线城市": 1.02, "三四线城市": 1.00},
    "被动履约型": {"一线城市": 0.72, "新一线城市": 0.88, "二线城市": 1.10, "三四线城市": 1.32},
}
AGE_MULT = {
    "主动筛查型": {"25-35岁": 1.05, "36-45岁": 1.18, "46-55岁": 1.12, "56岁以上": 0.88},
    "基础保障型": {"25-35岁": 1.00, "36-45岁": 1.00, "46-55岁": 1.00, "56岁以上": 1.00},
    "被动履约型": {"25-35岁": 0.92, "36-45岁": 0.86, "46-55岁": 0.94, "56岁以上": 1.18},
}
PAY_BASE = {
    "个人自费": {"主动筛查型": 0.52, "基础保障型": 0.38, "被动履约型": 0.10},
    "企业团检": {"主动筛查型": 0.16, "基础保障型": 0.54, "被动履约型": 0.30},
    "家庭套餐": {"主动筛查型": 0.26, "基础保障型": 0.57, "被动履约型": 0.17},
}

FREQ_BASE = {"主动筛查型": (1.70, 0.35, 1.0, 3.0),
             "基础保障型": (1.15, 0.25, 0.5, 2.0),
             "被动履约型": (0.85, 0.20, 0.3, 1.5)}
SPEND_BASE = {"主动筛查型": (1800, 520, 350, 800),
              "基础保障型": (900, 340, 280, 400),
              "被动履约型": (400, 280, 180, 200)}

# ----------------------------------------------------------------------------
# 3. 个体级数据生成
# ----------------------------------------------------------------------------
rows = []

for i in range(1, N + 1):
    age_group = pick(AGE_GROUPS, AGE_P)
    age_mid = AGE_MID[age_group]
    age = int(clamp(g(age_mid, 3.2), 25, 70))
    gender = pick(GENDERS, GENDER_P)
    male = 1 if gender == "男" else 0
    tier = pick(TIERS, TIER_P)
    tn = TIER_NUM[tier]
    occup = pick(OCCUPS, OCCUP_P)
    pay = pick(PAYS, PAY_P)
    city = random.choice(CITIES[tier])

    tier_bmi = [-0.55, -0.15, 0.15, 0.55][tn]
    occ_bmi = {"城市白领": -0.05, "企业管理层": 0.35, "高收入自由职业者": 0.15, "其他专业人群": -0.10}[occup]

    # ---- 核心生理指标 ----
    bmi_base = {"25-35岁": 23.25, "36-45岁": 24.05, "46-55岁": 24.55, "56岁以上": 24.65}[age_group]
    bmi = round(clamp(g(bmi_base + 0.85 * male + tier_bmi + occ_bmi, 3.05), 15.5, 40.0), 1)

    sbp_base = {"25-35岁": 116.5, "36-45岁": 122.0, "46-55岁": 130.5, "56岁以上": 137.5}[age_group]
    sbp = int(clamp(g(sbp_base + 3.5 * male + 2.2 * tier_bmi * -1 + 0.28 * (bmi - 24), 12.5), 85, 200))
    dbp_base = {"25-35岁": 72.5, "36-45岁": 75.5, "46-55岁": 78.5, "56岁以上": 80.5}[age_group]
    dbp = int(clamp(g(dbp_base + 2.5 * male + 1.0 * tier_bmi * -1 + 0.22 * (bmi - 24), 8.0), 55, 120))

    fpg_base = {"25-35岁": 5.10, "36-45岁": 5.28, "46-55岁": 5.52, "56岁以上": 5.78}[age_group]
    fpg = round(clamp(g(fpg_base + 0.10 * male + 0.08 * [-0.3, -0.1, 0.1, 0.3][tn]
                        + 0.012 * (bmi - 24), 0.55), 3.5, 15.0), 2)

    tc_base = {"25-35岁": 4.35, "36-45岁": 4.60, "46-55岁": 4.78, "56岁以上": 4.80}[age_group]
    tc = round(clamp(g(tc_base + 0.05 * male + 0.015 * (bmi - 24), 0.78), 2.5, 9.0), 2)
    tg_base = {"25-35岁": 0.92, "36-45岁": 1.06, "46-55岁": 1.18, "56岁以上": 1.20}[age_group]
    tg = round(clamp(g(tg_base + 0.16 * male + 0.030 * (bmi - 24), 0.45), 0.35, 7.0), 2)
    ldl_base = {"25-35岁": 2.50, "36-45岁": 2.72, "46-55岁": 2.86, "56岁以上": 2.88}[age_group]
    ldl = round(clamp(g(ldl_base + 0.05 * male + 0.012 * (bmi - 24), 0.66), 1.0, 6.5), 2)
    hdl_base = {"25-35岁": 1.52, "36-45岁": 1.48, "46-55岁": 1.44, "56岁以上": 1.42}[age_group]
    hdl = round(clamp(g(hdl_base - 0.12 * male - 0.006 * (bmi - 24), 0.22), 0.6, 2.5), 2)

    ua = int(clamp(g(280 + 1.30 * (age_mid - 30) + 78 * male + 9 * (bmi - 24)
                     + (-6 + 5 * tn), 62), 160, 700))

    # ---- 行为标签（受付费方式、城市线级、年龄段共同影响）----
    weights = []
    for lb in LABELS:
        weights.append(PAY_BASE[pay][lb] * TIER_MULT[lb][tier] * AGE_MULT[lb][age_group])
    total = sum(weights)
    weights = [w / total for w in weights]
    label = pick(LABELS, weights)

    # ---- 加项选择 ----
    addon_flags = {}
    for name, w in ADDON_ITEMS:
        if name.startswith("妇科") and male:
            addon_flags[name] = 0
            continue
        addon_flags[name] = 1 if random.random() < w[label] * (0.90 + 0.25 * random.random()) else 0
    addon_count = sum(addon_flags.values())

    f_mu, f_sd, f_lo, f_hi = FREQ_BASE[label]
    freq = round(clamp(g(f_mu, f_sd), f_lo, f_hi), 2)
    s_base, s_unit, s_sd, s_lo = SPEND_BASE[label]
    spend = int(clamp(g(s_base + s_unit * addon_count, s_sd), s_lo, 20000))

    # ---- 指标异常判定 ----
    f_overweight = 1 if bmi >= 24 else 0
    f_obese = 1 if bmi >= 28 else 0
    f_hbp = 1 if (sbp >= 140 or dbp >= 90) else 0          # 高血压
    f_bp_high = 1 if (sbp >= 130 or dbp >= 85) else 0      # 血压偏高（含正常高值）
    f_glu = 1 if fpg >= 6.1 else 0                          # 空腹血糖偏高
    f_lipid = 1 if (tc >= 5.2 or tg >= 1.7 or ldl >= 3.4 or hdl < 1.0) else 0
    ua_thr = 420 if male else 360
    f_ua = 1 if ua > ua_thr else 0

    age_e = {"25-35岁": -0.05, "36-45岁": 0.0, "46-55岁": 0.06, "56岁以上": 0.08}[age_group]
    tier_e = [-0.06, -0.02, 0.02, 0.07][tn]
    label_e = {"主动筛查型": 0.09, "基础保障型": 0.02, "被动履约型": -0.03}[label]
    ldct = addon_flags["低剂量胸部CT"]

    def flag(p):
        return 1 if random.random() < p else 0

    f_fatty = flag(prob(0.29, age_e, 0.10 * male, 0.05 * (bmi - 24),
                        [-0.02, -0.01, 0.02, 0.04][tn],
                        0.03 if occup == "企业管理层" else 0.0))
    f_thyroid = flag(prob(0.27, 0.6 * age_e, 0.10 * (1 - male),
                          [0.05, 0.02, -0.01, -0.04][tn], label_e))
    f_lung = flag(prob(0.095, 0.55 * age_e, 0.05 * male, 0.18 * ldct,
                       [0.03, 0.01, -0.01, -0.02][tn]))
    f_hp = flag(prob(0.27, tier_e, 0.5 * age_e, -0.03 if pay == "个人自费" else 0.0))
    f_alt = flag(prob(0.095, 0.045 * (bmi - 24), 0.08 * male, 0.02 * (f_fatty)))
    f_ecg = flag(prob(0.16, 0.75 * age_e, 0.03 * male))
    f_bone = flag(prob(0.10, 0.085 * (age_mid - 30) / 10, 0.08 * (1 - male),
                       -0.04 if label == "主动筛查型" else 0.0))
    f_sleep = flag(prob(0.30, [0.05, 0.03, -0.01, -0.04][tn],
                        0.06 if occup == "企业管理层" else 0.0,
                        -0.02 * (1 - male)))
    f_neck = flag(prob(0.44, 0.04 * (age_mid - 30) / 10,
                       0.08 if occup in ("城市白领", "企业管理层") else 0.0,
                       -0.05 * male))
    f_vision = flag(prob(0.62, 0.10 if occup == "城市白领" else 0.0, -0.05 * male))
    f_breast = 0 if male else flag(prob(0.55, 0.3 * age_e))
    f_prostate = flag(prob(0.33, 0.85 * age_e)) if male else 0
    f_gastritis = flag(prob(0.09, 0.25 * f_hp, 0.02 * male))
    f_stone = flag(prob(0.075, 0.028 * (age_mid - 30) / 10, 0.04 * male))
    f_anemia = 0 if male else flag(prob(0.11, -0.02 * (bmi - 24)))

    rows.append({
        "记录ID": f"HNW{i:05d}",
        "年龄段": age_group,
        "年龄": age,
        "性别": gender,
        "城市线级": tier,
        "城市": city,
        "职业类型": occup,
        "付费方式": pay,
        "BMI": bmi,
        "收缩压": sbp,
        "舒张压": dbp,
        "空腹血糖": fpg,
        "总胆固醇": tc,
        "甘油三酯": tg,
        "低密度脂蛋白": ldl,
        "高密度脂蛋白": hdl,
        "血尿酸": ua,
        "体检频次_次每年": freq,
        "加项数量": addon_count,
        "次均消费_元": spend,
        "行为标签": label,
        "超重或肥胖": f_overweight,
        "肥胖_BMI28以上": f_obese,
        "高血压": f_hbp,
        "血压偏高": f_bp_high,
        "空腹血糖偏高": f_glu,
        "血脂异常": f_lipid,
        "尿酸偏高": f_ua,
        "脂肪肝": f_fatty,
        "甲状腺结节": f_thyroid,
        "肺结节": f_lung,
        "幽门螺杆菌阳性": f_hp,
        "转氨酶升高": f_alt,
        "心电图异常": f_ecg,
        "骨量减少": f_bone,
        "睡眠障碍": f_sleep,
        "颈肩腰不适": f_neck,
        "视力问题": f_vision,
        "乳腺增生": f_breast,
        "前列腺异常": f_prostate,
        "慢性胃炎": f_gastritis,
        "胆肾结石或囊肿": f_stone,
        "贫血倾向": f_anemia,
        **{f"加项_{k}": v for k, v in addon_flags.items()},
    })

# ----------------------------------------------------------------------------
# 4. 写出个体级 CSV
# ----------------------------------------------------------------------------
csv_path = os.path.join(BASE_DIR, "hnw_health_dataset_simulated.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

# ----------------------------------------------------------------------------
# 5. 聚合统计
# ----------------------------------------------------------------------------
def rate(subset, key):
    if not subset:
        return 0.0
    return round(100.0 * sum(r[key] for r in subset) / len(subset), 1)


def avg(subset, key, nd=2):
    if not subset:
        return 0.0
    return round(sum(r[key] for r in subset) / len(subset), nd)


# 全国参考值（公开流行病学资料）
NAT = {
    "超重或肥胖": 50.7, "血压偏高": 41.0, "高血压": 27.5, "空腹血糖偏高": 12.4,
    "血脂异常": 40.4, "脂肪肝": 29.6, "甲状腺结节": 22.0, "尿酸偏高": 13.3,
    "幽门螺杆菌阳性": 40.0, "肺结节": 8.0, "转氨酶升高": 12.0, "心电图异常": 14.0,
    "骨量减少": 20.0, "睡眠障碍": 20.0, "颈肩腰不适": 38.0, "视力问题": 55.0,
    "乳腺增生": 48.0, "前列腺异常": 29.0, "慢性胃炎": 17.0, "胆肾结石或囊肿": 10.0,
    "贫血倾向": 14.0,
}

CORE_METRICS = [
    ("BMI", "kg/m²", "超重或肥胖"),
    ("收缩压", "mmHg", "血压偏高"),
    ("空腹血糖", "mmol/L", "空腹血糖偏高"),
    ("总胆固醇", "mmol/L", "血脂异常"),
]

core = []
for col, unit, flag_key in CORE_METRICS:
    vals = [r[col] for r in rows]
    core.append({
        "指标": col,
        "单位": unit,
        "均值": round(sum(vals) / len(vals), 2),
        "中位数": round(pct(vals, 0.5), 2),
        "P25": round(pct(vals, 0.25), 2),
        "P75": round(pct(vals, 0.75), 2),
        "异常维度": flag_key,
        "检出率": rate(rows, flag_key),
        "全国参考": NAT[flag_key],
        "偏差": round(rate(rows, flag_key) - NAT[flag_key], 1),
    })

# 核心四项复合指标：本群 vs 全国
core_compare = [
    {"名称": "超重或肥胖", "本群": rate(rows, "超重或肥胖"), "全国": NAT["超重或肥胖"]},
    {"名称": "血压偏高", "本群": rate(rows, "血压偏高"), "全国": NAT["血压偏高"]},
    {"名称": "空腹血糖偏高", "本群": rate(rows, "空腹血糖偏高"), "全国": NAT["空腹血糖偏高"]},
    {"名称": "血脂异常", "本群": rate(rows, "血脂异常"), "全国": NAT["血脂异常"]},
    {"名称": "高血压", "本群": rate(rows, "高血压"), "全国": NAT["高血压"]},
]
for c in core_compare:
    c["偏差"] = round(c["本群"] - c["全国"], 1)

CORE_KEYS = ["超重或肥胖", "血压偏高", "空腹血糖偏高", "血脂异常"]
SHORT = {"超重或肥胖": "超重/肥胖", "血压偏高": "血压偏高",
         "空腹血糖偏高": "血糖偏高", "血脂异常": "血脂异常"}

# 分层：年龄段
age_strata = []
for ag in AGE_GROUPS:
    sub = [r for r in rows if r["年龄段"] == ag]
    age_strata.append({
        "分层": ag,
        "样本占比": round(100.0 * len(sub) / len(rows), 1),
        "次均消费": avg(sub, "次均消费_元", 0),
        "体检频次": avg(sub, "体检频次_次每年", 2),
        "值": {SHORT[k]: rate(sub, k) for k in CORE_KEYS},
    })

# 分层：城市线级
tier_strata = []
for t in TIERS:
    sub = [r for r in rows if r["城市线级"] == t]
    tier_strata.append({
        "分层": t,
        "城市数": len(CITIES[t]),
        "样本城市数": len(set(r["城市"] for r in sub)),
        "样本占比": round(100.0 * len(sub) / len(rows), 1),
        "次均消费": avg(sub, "次均消费_元", 0),
        "体检频次": avg(sub, "体检频次_次每年", 2),
        "值": {SHORT[k]: rate(sub, k) for k in CORE_KEYS},
    })

# 分层：性别
gender_strata = []
for gd in GENDERS:
    sub = [r for r in rows if r["性别"] == gd]
    gender_strata.append({
        "分层": gd,
        "样本占比": round(100.0 * len(sub) / len(rows), 1),
        "次均消费": avg(sub, "次均消费_元", 0),
        "值": {SHORT[k]: rate(sub, k) for k in CORE_KEYS},
    })

# TOP 20 健康异常榜单
TOP20_KEYS = [
    ("超重或肥胖", "代谢"), ("视力问题", "生活方式"), ("颈肩腰不适", "生活方式"),
    ("血脂异常", "代谢"), ("脂肪肝", "代谢"), ("甲状腺结节", "筛查相关"),
    ("血压偏高", "心血管"), ("睡眠障碍", "生活方式"), ("尿酸偏高", "代谢"),
    ("高血压", "心血管"), ("肺结节", "筛查相关"), ("骨量减少", "骨骼"),
    ("心电图异常", "心血管"), ("幽门螺杆菌阳性", "感染"), ("转氨酶升高", "代谢"),
    ("空腹血糖偏高", "代谢"), ("慢性胃炎", "消化"), ("胆肾结石或囊肿", "消化"),
    ("乳腺增生", "性别特异"), ("前列腺异常", "性别特异"), ("贫血倾向", "性别特异"),
]
top20 = []
for key, cat in TOP20_KEYS:
    if key in ("乳腺增生", "贫血倾向"):
        sub = [r for r in rows if r["性别"] == "女"]
        scope = "女性"
    elif key == "前列腺异常":
        sub = [r for r in rows if r["性别"] == "男"]
        scope = "男性"
    else:
        sub = rows
        scope = "全样本"
    top20.append({
        "问题": key,
        "类别": cat,
        "口径": scope,
        "检出率": rate(sub, key),
        "全国": NAT[key],
        "偏差": round(rate(sub, key) - NAT[key], 1),
    })
top20.sort(key=lambda x: -x["检出率"])
top20 = top20[:20]
for i, t in enumerate(top20, 1):
    t["排名"] = i

# 行为分层
behavior = []
for lb in LABELS:
    sub = [r for r in rows if r["行为标签"] == lb]
    behavior.append({
        "标签": lb,
        "占比": round(100.0 * len(sub) / len(rows), 1),
        "人数": len(sub),
        "体检频次": avg(sub, "体检频次_次每年", 2),
        "加项数量": avg(sub, "加项数量", 2),
        "次均消费": avg(sub, "次均消费_元", 0),
        "个人自费占比": round(100.0 * sum(1 for r in sub if r["付费方式"] == "个人自费") / len(sub), 1),
        "平均年龄": avg(sub, "年龄", 1),
        "一线及新一线占比": round(100.0 * sum(1 for r in sub if r["城市线级"] in ("一线城市", "新一线城市")) / len(sub), 1),
        "年龄结构": {ag: round(100.0 * sum(1 for r in sub if r["年龄段"] == ag) / len(sub), 1) for ag in AGE_GROUPS},
        "城市结构": {t: round(100.0 * sum(1 for r in sub if r["城市线级"] == t) / len(sub), 1) for t in TIERS},
        "血脂异常率": rate(sub, "血脂异常"),
        "脂肪肝率": rate(sub, "脂肪肝"),
    })

# 加项偏好
addons = []
for name, _w in ADDON_ITEMS:
    col = f"加项_{name}"
    if name.startswith("妇科"):
        sub = [r for r in rows if r["性别"] == "女"]
        denom = len(sub)
    else:
        sub = rows
        denom = len(rows)
    addons.append({
        "项目": name,
        "整体": round(100.0 * sum(r[col] for r in sub) / denom, 1),
        "主动筛查型": round(100.0 * sum(r[col] for r in sub if r["行为标签"] == "主动筛查型")
                          / max(1, sum(1 for r in sub if r["行为标签"] == "主动筛查型")), 1),
        "基础保障型": round(100.0 * sum(r[col] for r in sub if r["行为标签"] == "基础保障型")
                          / max(1, sum(1 for r in sub if r["行为标签"] == "基础保障型")), 1),
        "被动履约型": round(100.0 * sum(r[col] for r in sub if r["行为标签"] == "被动履约型")
                          / max(1, sum(1 for r in sub if r["行为标签"] == "被动履约型")), 1),
    })
addons.sort(key=lambda x: -x["整体"])

# BMI 分布
bmi_bins = []
lo = 16
while lo < 36:
    hi = lo + 1
    cnt = sum(1 for r in rows if lo <= r["BMI"] < hi)
    bmi_bins.append({"区间": f"{lo}-{hi}", "人数": cnt,
                     "占比": round(100.0 * cnt / len(rows), 1)})
    lo = hi

# 城市 TOP（样本量）
city_counter = {}
for r in rows:
    city_counter.setdefault((r["城市"], r["城市线级"]), 0)
    city_counter[(r["城市"], r["城市线级"])] += 1
city_top = sorted(
    [{"城市": k[0], "线级": k[1], "样本量": v} for k, v in city_counter.items()],
    key=lambda x: -x["样本量"])[:15]

# 消费分层
spend_bins = [(0, 800), (800, 1500), (1500, 2500), (2500, 4000), (4000, 100000)]
spend_labels = ["<800元", "800-1500元", "1500-2500元", "2500-4000元", "4000元以上"]
spend_dist = []
for (lo_, hi_), lab in zip(spend_bins, spend_labels):
    cnt = sum(1 for r in rows if lo_ <= r["次均消费_元"] < hi_)
    spend_dist.append({"区间": lab, "占比": round(100.0 * cnt / len(rows), 1)})

# 职业 × 消费
occup_stat = []
for o in OCCUPS:
    sub = [r for r in rows if r["职业类型"] == o]
    occup_stat.append({
        "职业": o,
        "占比": round(100.0 * len(sub) / len(rows), 1),
        "次均消费": avg(sub, "次均消费_元", 0),
        "体检频次": avg(sub, "体检频次_次每年", 2),
        "主动筛查占比": round(100.0 * sum(1 for r in sub if r["行为标签"] == "主动筛查型") / len(sub), 1),
        "血脂异常率": rate(sub, "血脂异常"),
        "脂肪肝率": rate(sub, "脂肪肝"),
    })

# 付费方式
pay_stat = [{"方式": p,
             "占比": round(100.0 * sum(1 for r in rows if r["付费方式"] == p) / len(rows), 1),
             "次均消费": avg([r for r in rows if r["付费方式"] == p], "次均消费_元", 0)}
            for p in PAYS]

stats = {
    "meta": {
        "样本量": N,
        "覆盖城市": CITY_POOL_SIZE,
        "样本覆盖城市数": len(set(r["城市"] for r in rows)),
        "数据源": "SelectDataset 数据产品交易市场 · 高净值人群健康画像数据集（产品编号 141）",
        "供方": "上海数据发展科技有限责任公司",
        "上架时间": "2026-06-23",
        "声明": "图表数据为基于数据集公开口径构建的模拟演示数据，非真实成交数据",
    },
    "overview": {
        "个人自费占比": round(100.0 * sum(1 for r in rows if r["付费方式"] == "个人自费") / len(rows), 1),
        "平均年龄": avg(rows, "年龄", 1),
        "次均消费": avg(rows, "次均消费_元", 0),
        "平均体检频次": avg(rows, "体检频次_次每年", 2),
        "平均加项数": avg(rows, "加项数量", 2),
        "至少一项异常": round(100.0 * sum(
            1 for r in rows if any(r[k] for k in ["超重或肥胖", "血压偏高", "空腹血糖偏高",
                                                  "血脂异常", "脂肪肝", "甲状腺结节", "尿酸偏高",
                                                  "幽门螺杆菌阳性", "肺结节", "转氨酶升高"])) / len(rows), 1),
    },
    "core": core,
    "core_compare": core_compare,
    "age_strata": age_strata,
    "tier_strata": tier_strata,
    "gender_strata": gender_strata,
    "top20": top20,
    "behavior": behavior,
    "addons": addons,
    "bmi_bins": bmi_bins,
    "city_top": city_top,
    "spend_dist": spend_dist,
    "occup_stat": occup_stat,
    "pay_stat": pay_stat,
}

with open(os.path.join(BASE_DIR, "dashboard_data.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

# ----------------------------------------------------------------------------
# 6. 控制台校验输出
# ----------------------------------------------------------------------------
print(f"样本量: {N}   城市: {stats['meta']['覆盖城市']}   个人自费: {stats['overview']['个人自费占比']}%")
print(f"次均消费: {stats['overview']['次均消费']}元   频次: {stats['overview']['平均体检频次']}次/年"
      f"   加项: {stats['overview']['平均加项数']}项   至少一项异常: {stats['overview']['至少一项异常']}%")
print("\n-- 核心指标 --")
for c in core:
    print(f"{c['指标']:<8} 均值{c['均值']:>6}  中位{c['中位数']:>6}  "
          f"{c['异常维度']}: {c['检出率']}% (全国{c['全国参考']}%, {c['偏差']:+.1f}pp)")
print("\n-- 复合指标对比 --")
for c in core_compare:
    print(f"{c['名称']:<10} 本群{c['本群']:>6}%  全国{c['全国']:>6}%  {c['偏差']:+.1f}pp")
print("\n-- TOP20 榜单 --")
for t in top20:
    print(f"{t['排名']:>2}. {t['问题']:<12}({t['口径']}) {t['检出率']:>5}%  全国{t['全国']:>5}%  {t['偏差']:+.1f}pp")
print("\n-- 行为分层 --")
for b in behavior:
    print(f"{b['标签']:<6} 占比{b['占比']:>5}%  频次{b['体检频次']}  加项{b['加项数量']}  "
          f"客单{b['次均消费']}元  自费{b['个人自费占比']}%  一线新一线{b['一线及新一线占比']}%")
print("\n-- 年龄段 --")
for a in age_strata:
    print(f"{a['分层']:<8} 占比{a['样本占比']:>5}%  " + "  ".join(f"{k}{v}%" for k, v in a["值"].items()))
print("\n-- 城市线级 --")
for a in tier_strata:
    print(f"{a['分层']:<8} 占比{a['样本占比']:>5}%  客单{a['次均消费']}元  "
          + "  ".join(f"{k}{v}%" for k, v in a["值"].items()))
print("\n-- 加项偏好 --")
for a in addons:
    print(f"{a['项目']:<28} {a['整体']:>5}%  主动{a['主动筛查型']:>5}%  基础{a['基础保障型']:>5}%  被动{a['被动履约型']:>5}%")
print("\n-- 消费分布 --")
for s in spend_dist:
    print(f"{s['区间']:<12} {s['占比']}%")
