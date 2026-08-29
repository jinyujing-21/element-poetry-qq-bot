-- 元素之诗索引系统 — 数据库初始化
-- 所有模块独立建表，别名系统共享

-- ========== 公共表 ==========

-- 别名表
CREATE TABLE IF NOT EXISTS aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT NOT NULL,
    standard_name TEXT NOT NULL,
    module TEXT NOT NULL,
    target_id INTEGER,
    priority INTEGER DEFAULT 0,
    is_verified INTEGER DEFAULT 0,
    UNIQUE(alias, module)
);

-- 查询日志
CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    group_id TEXT,
    raw_input TEXT,
    resolved_name TEXT,
    module TEXT,
    hit INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 反馈表
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    group_id TEXT,
    content TEXT,
    module TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== Boss 属性表 ==========
CREATE TABLE IF NOT EXISTS boss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dungeon TEXT,
    difficulty TEXT,
    stage TEXT,
    phys_reduce TEXT,
    magic_reduce TEXT,
    fire_res INTEGER,
    light_res INTEGER,
    thunder_res INTEGER,
    water_res INTEGER,
    wind_res INTEGER,
    attack_element TEXT,
    is_broken INTEGER DEFAULT 0,
    is_estimated INTEGER DEFAULT 0,
    source TEXT,
    version_date TEXT,
    notes TEXT
);

-- ========== 进本条件表 ==========
CREATE TABLE IF NOT EXISTS dungeon_entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    alias TEXT,
    dungeon_type TEXT,
    difficulty TEXT,
    min_level INTEGER,
    min_combat_c INTEGER,
    min_combat_n INTEGER,
    min_combat_t INTEGER,
    recommend_party_size TEXT,
    class_requirement TEXT,
    must_mechanic TEXT,
    must_item TEXT,
    prerequisite TEXT,
    version_date TEXT,
    notes TEXT
);

-- ========== 自强战力推荐表 ==========
CREATE TABLE IF NOT EXISTS dungeon_solo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dungeon_name TEXT NOT NULL,
    difficulty TEXT,
    recommend_c INTEGER,
    recommend_n INTEGER,
    recommend_t INTEGER,
    class_notes TEXT,
    mechanic_notes TEXT,
    is_nightmare INTEGER DEFAULT 0,
    party_size TEXT,
    version_date TEXT,
    contributor TEXT,
    confidence TEXT DEFAULT '人工整理'
);

-- ========== 纹章表 ==========
CREATE TABLE IF NOT EXISTS seal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class_name TEXT,
    branch TEXT,
    seal_type TEXT,
    effect TEXT,
    how_to_get TEXT,
    image_path TEXT,
    version_date TEXT,
    notes TEXT
);

-- ========== 锻造配方表 ==========
CREATE TABLE IF NOT EXISTS forge_recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_item TEXT NOT NULL,
    target_quantity INTEGER DEFAULT 1,
    material_name TEXT NOT NULL,
    material_quantity INTEGER NOT NULL,
    is_prerequisite INTEGER DEFAULT 0,
    gold_cost INTEGER DEFAULT 0,
    magic_cost INTEGER DEFAULT 0,
    version_date TEXT
);

-- ========== 锻造装备信息表 ==========
CREATE TABLE IF NOT EXISTS forge_equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    equip_type TEXT,
    class_limit TEXT,
    stage TEXT,
    forge_location TEXT,
    forge_npc TEXT,
    is_upgradeable INTEGER DEFAULT 0,
    version_date TEXT,
    notes TEXT
);

-- ========== 魔素解构表 ==========
CREATE TABLE IF NOT EXISTS magic_decompose (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    item_type TEXT,
    product_name TEXT NOT NULL,
    product_quantity INTEGER,
    magic_level TEXT,
    conversion_rate TEXT,
    can_decompose INTEGER DEFAULT 1,
    is_recommended INTEGER DEFAULT 0,
    version_date TEXT,
    notes TEXT
);

-- ========== Wiki 同步记录 ==========
CREATE TABLE IF NOT EXISTS wiki_sync (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_title TEXT NOT NULL,
    page_url TEXT,
    last_synced TIMESTAMP,
    sync_status TEXT,
    local_table TEXT,
    local_id INTEGER
);

-- ========== 索引 ==========
CREATE INDEX IF NOT EXISTS idx_aliases_alias ON aliases(alias);
CREATE INDEX IF NOT EXISTS idx_aliases_module ON aliases(module);
CREATE INDEX IF NOT EXISTS idx_boss_name ON boss(name);
CREATE INDEX IF NOT EXISTS idx_boss_dungeon ON boss(dungeon);
CREATE INDEX IF NOT EXISTS idx_dungeon_entry_name ON dungeon_entry(name);
CREATE INDEX IF NOT EXISTS idx_dungeon_solo_name ON dungeon_solo(dungeon_name);
CREATE INDEX IF NOT EXISTS idx_seal_name ON seal(name);
CREATE INDEX IF NOT EXISTS idx_seal_class ON seal(class_name);
CREATE INDEX IF NOT EXISTS idx_forge_recipe_target ON forge_recipe(target_item);
CREATE INDEX IF NOT EXISTS idx_forge_equipment_name ON forge_equipment(name);
CREATE INDEX IF NOT EXISTS idx_magic_decompose_item ON magic_decompose(item_name);
