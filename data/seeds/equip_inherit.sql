-- 装备继承关系表
CREATE TABLE IF NOT EXISTS equip_inherit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_equip TEXT NOT NULL,
    to_equip TEXT NOT NULL,
    material TEXT NOT NULL,
    level_loss TEXT NOT NULL,
    notes TEXT
);

-- 插入装备继承数据
INSERT INTO equip_inherit (from_equip, to_equip, material, level_loss, notes) VALUES
-- 主线继承
('海妖', '黑钢', '黑钢·熔炉之魂', '完美继承', ''),
('黑钢', '焱祭', '焱祭·熔炉之魂', '等级-5', ''),
('焱祭', '骸骨', '骸骨·熔炉之魂', '等级-2', ''),
('骸骨', '劫影', '劫影·熔炉之魂', '等级-5', ''),
('劫影', '罗刹', '罗刹·熔炉之魂', '等级-5', ''),
('罗刹', '古藤', '古藤·熔炉之魂', '等级-5', ''),

-- 分支继承
('焱祭', '血源', '血源·熔炉之魂', '等级-2', ''),
('骸骨', '血源', '血源·熔炉之魂', '等级-3', ''),
('血源', '罗刹', '罗刹·熔炉之魂', '等级-6', ''),
('劫影', '罗刹', '罗刹·熔炉之魂', '等级-5', ''),
('劫影', '缚灵', '缚灵·熔炉之魂', '等级-2', ''),
('血源', '缚灵', '缚灵·熔炉之魂', '等级-3', ''),
('缚灵', '古藤', '古藤·熔炉之魂', '等级-6', ''),
('罗刹', '古藤', '古藤·熔炉之魂', '等级-5', '');

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_equip_inherit_from ON equip_inherit(from_equip);
CREATE INDEX IF NOT EXISTS idx_equip_inherit_to ON equip_inherit(to_equip);
