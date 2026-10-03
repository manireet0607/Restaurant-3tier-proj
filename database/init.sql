-- Dragon Wok: MySQL 8.0+ schema and sample data.
-- Optional. The normal path is Alembic (alembic upgrade head) + the seed script.
-- Use this file if you want to set up the database by hand, for example on a fresh RDS instance:
--   mysql -h <host> -u <user> -p --ssl-ca=global-bundle.pem --ssl-mode=VERIFY_IDENTITY dragonwok < database/init.sql
-- Create the first admin separately (needs a bcrypt hash): run `python -m app.db.seed` with ADMIN_PASSWORD set.

CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'customer',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY ix_users_email (email),
  CONSTRAINT ck_users_role CHECK (role IN ('customer', 'admin'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS categories (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS menu_items (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  name VARCHAR(150) NOT NULL,
  description TEXT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  image_url VARCHAR(500) NULL,
  food_type VARCHAR(10) NOT NULL,
  is_available TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY ix_menu_items_category_id (category_id),
  CONSTRAINT fk_menu_items_category FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT,
  CONSTRAINT ck_menu_items_price_nonneg CHECK (price >= 0),
  CONSTRAINT ck_menu_items_food_type CHECK (food_type IN ('veg', 'non_veg'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS orders (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  order_number VARCHAR(30) NOT NULL UNIQUE,
  subtotal DECIMAL(10,2) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  delivery_fee DECIMAL(10,2) NOT NULL,
  tax_amount DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(20) NOT NULL DEFAULT 'cod',
  payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
  order_status VARCHAR(20) NOT NULL DEFAULT 'pending',
  customer_name VARCHAR(100) NOT NULL,
  customer_phone VARCHAR(20) NOT NULL,
  delivery_address TEXT NOT NULL,
  special_instructions TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY ix_orders_user_id (user_id),
  KEY ix_orders_order_status (order_status),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT,
  CONSTRAINT ck_orders_payment_method CHECK (payment_method IN ('cod')),
  CONSTRAINT ck_orders_payment_status CHECK (payment_status IN ('pending', 'paid', 'failed')),
  CONSTRAINT ck_orders_status CHECK (order_status IN ('pending','confirmed','preparing','out_for_delivery','delivered','cancelled'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS order_items (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  menu_item_id INT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,   -- price when the order was placed
  subtotal DECIMAL(10,2) NOT NULL,
  KEY ix_order_items_order_id (order_id),
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  CONSTRAINT fk_order_items_menu_item FOREIGN KEY (menu_item_id) REFERENCES menu_items (id) ON DELETE RESTRICT,
  CONSTRAINT ck_order_items_qty_positive CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---- Sample data ----
INSERT IGNORE INTO categories (name, description) VALUES
 ('Chinese Starters', 'Crispy and spicy openers'),
 ('Noodles', 'Wok-tossed Hakka noodles'),
 ('Fried Rice', 'Smoky wok fried rice'),
 ('Chinese Main Course', 'Rich gravies and dry dishes'),
 ('Soups', 'Hot and comforting bowls'),
 ('Momos', 'Steamed and fried dumplings'),
 ('Desserts', 'Sweet endings'),
 ('Beverages', 'Cool drinks');

INSERT INTO menu_items (category_id, name, description, price, image_url, food_type)
SELECT c.id, v.name, v.description, v.price, v.image_url, v.food_type FROM (
  SELECT 'Noodles' cat, 'Veg Hakka Noodles' name, 'Wok-tossed noodles with crunchy cabbage, carrot and capsicum.' description, 180.00 price, '/images/noodles.svg' image_url, 'veg' food_type
  UNION ALL SELECT 'Noodles', 'Chicken Hakka Noodles', 'Smoky noodles tossed with tender chicken and vegetables.', 220.00, '/images/noodles.svg', 'non_veg'
  UNION ALL SELECT 'Fried Rice', 'Veg Fried Rice', 'Fragrant rice fried on high heat with fresh vegetables.', 170.00, '/images/rice.svg', 'veg'
  UNION ALL SELECT 'Fried Rice', 'Chicken Fried Rice', 'Wok fried rice with egg, chicken and spring onion.', 210.00, '/images/rice.svg', 'non_veg'
  UNION ALL SELECT 'Chinese Starters', 'Chilli Paneer', 'Crispy paneer cubes in a spicy garlic soy glaze.', 240.00, '/images/starters.svg', 'veg'
  UNION ALL SELECT 'Chinese Starters', 'Chilli Chicken', 'Crispy chicken tossed with capsicum and green chilli.', 280.00, '/images/starters.svg', 'non_veg'
  UNION ALL SELECT 'Chinese Starters', 'Spring Rolls', 'Golden crispy rolls filled with vegetables, with sweet chilli dip.', 150.00, '/images/starters.svg', 'veg'
  UNION ALL SELECT 'Chinese Main Course', 'Veg Manchurian', 'Vegetable dumplings in a rich Manchurian gravy.', 200.00, '/images/main.svg', 'veg'
  UNION ALL SELECT 'Chinese Main Course', 'Chicken Manchurian', 'Chicken balls simmered in a tangy, garlicky Manchurian gravy.', 260.00, '/images/main.svg', 'non_veg'
  UNION ALL SELECT 'Soups', 'Hot and Sour Soup', 'Peppery and tangy soup with vegetables and tofu.', 130.00, '/images/soups.svg', 'veg'
  UNION ALL SELECT 'Momos', 'Veg Momos', 'Steamed dumplings stuffed with cabbage, carrot and herbs.', 120.00, '/images/momos.svg', 'veg'
  UNION ALL SELECT 'Momos', 'Chicken Momos', 'Juicy steamed dumplings with spiced chicken filling.', 150.00, '/images/momos.svg', 'non_veg'
  UNION ALL SELECT 'Desserts', 'Chocolate Brownie', 'Warm fudgy brownie with chocolate sauce.', 140.00, '/images/desserts.svg', 'veg'
  UNION ALL SELECT 'Beverages', 'Cold Coffee', 'Chilled creamy coffee blended with ice cream.', 110.00, '/images/beverages.svg', 'veg'
) v JOIN categories c ON c.name = v.cat
WHERE NOT EXISTS (SELECT 1 FROM menu_items m WHERE m.name = v.name);
