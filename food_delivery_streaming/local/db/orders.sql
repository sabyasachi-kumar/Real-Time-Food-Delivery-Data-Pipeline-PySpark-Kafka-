CREATE TABLE public.dsai2025em1100189_orders (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255),
    restaurant_name VARCHAR(255),
    item VARCHAR(255),
    amount NUMERIC,
    order_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert 10 initial historical sample records
INSERT INTO public.dsai2025em1100189_orders
(customer_name, restaurant_name, item, amount, order_status, created_at)
VALUES
('Rahul Sharma', 'Dominos', 'Farmhouse Pizza', 450, 'PLACED',      '2025-12-01 10:00:00'),
('Suman Roy',   'KFC',     'Zinger Burger',    230, 'DELIVERED',   '2025-12-01 10:02:00'),
('Priya Singh', 'Subway',  'Veg Sub',          180, 'PREPARING',   '2025-12-01 10:03:00'),
('Arun Kumar',  'McDonalds','McFlurry',        120, 'CANCELLED',   '2025-12-01 10:04:00'),
('Manish Das',  'Pizza Hut','Garlic Bread',    200, 'DELIVERED',   '2025-12-01 10:05:00'),
('Amrita Sen',  'Wow Momo','Chicken Momo',     160, 'PLACED',      '2025-12-01 10:06:00'),
('Karan Patel', 'Burger King','Whopper',       320, 'PREPARING',   '2025-12-01 10:07:00'),
('Reema Verma', 'Taco Bell','Veg Taco',        140, 'DELIVERED',   '2025-12-01 10:08:00'),
('Jaspreet Singh','Bikanervala','Thali Meal',  280, 'PLACED',      '2025-12-01 10:09:00'),
('Nikhil Gupta', 'Barbeque Nation','BBQ Platter',650,'PREPARING',  '2025-12-01 10:10:00');
