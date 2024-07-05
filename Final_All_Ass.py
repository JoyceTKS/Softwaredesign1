import sqlite3
import tkinter.messagebox as messagebox
from tkinter import Tk, StringVar, Frame, Label, Entry, Button, Toplevel, Canvas, filedialog
import random
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime, date
from fpdf import FPDF
import subprocess
from tkcalendar import DateEntry

root = Tk()
root.title("Home Page")
root.geometry("1920x1080+0+0")
root.state("zoomed")

# Constants
WIDTH = 800
HEIGHT = 700

# Create variables
USERNAME_LOGIN = StringVar()
PASSWORD_LOGIN = StringVar()
USERNAME_REGISTER = StringVar()
PASSWORD_REGISTER = StringVar()
FIRST_NAME = StringVar()
LAST_NAME = StringVar()
DATE_OF_BIRTH = StringVar()
EMAIL_ADDRESS = StringVar()
CONFIRM_PASSWORD = StringVar()

STAFF_LOGIN = StringVar()
STAFF_PASSWORD_LOGIN = StringVar()
STAFF_REGISTER = StringVar()
STAFF_PASSWORD_REGISTER = StringVar()
POSITION = StringVar()

conn = sqlite3.connect('db_member.db')
cursor = conn.cursor()


def create_homepage():
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Load the background image
    background_image = Image.open("C:/Kai Shuang/Background.jpg")
    if background_image.size != (1920, 1080):
        background_image = background_image.resize((1920, 1080))
    background_photo = ImageTk.PhotoImage(background_image)

    # Create Canvas and set the background image
    canvas = Canvas(root, width=1920, height=1080)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor=tk.NW, image=background_photo)

    # Create LabelFrame as the main content area
    frame = LabelFrame(canvas, text="Welcome to Blueday Restaurant!", font=('Cascadia Code SemiBold', 20),
                       fg='darkblue',
                       padx=150, pady=150, bg='lightsteelblue')
    frame.place(x=515, y=100)

    # Create and place buttons
    customer_button = Button(frame, text="Customer", command=LoginForm, font=('times new roman', 20, 'bold'), bd=18,
                             bg='grey', width=9)
    staff_button = Button(frame, text="Staff", command=StaffLoginForm, font=('times new roman', 20, 'bold'), bd=18,
                          bg='grey', width=9)

    customer_button.pack()
    staff_button.pack(pady=30)

    # Retain a reference to the background image to prevent garbage collection
    canvas.background_photo = background_photo


def Database():
    global conn, cursor
    conn = sqlite3.connect("db_member.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `Customer` (customer_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Username TEXT, "
        "Password TEXT, First_Name TEXT, Last_Name TEXT, Date_Of_Birth TEXT, Email_Address TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `ADMIN` (admin_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Staff_Name TEXT, "
        "Password TEXT, Position TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `food` (food_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, food_name TEXT, "
        "description TEXT, price FLOAT, food_category TEXT, Image_Path TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `Orders` (order_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, order_date DATE, remark TEXT, order_total FLOAT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `OrderDetails` (order_detail_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, order_id INTEGER, food_name TEXT, price FLOAT, FOREIGN KEY (order_id) REFERENCES Orders(order_id))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `Payment` (payment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, order_id INTEGER, Payment_Date DATE, Total_price FLOAT, FOREIGN KEY (order_id) REFERENCES Orders(order_id))"
    )
    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()


def Menu():
    global MenuHomePageFrame, conn, cursor, TopBannerImage, displayDefaultImage
    root.withdraw()
    MenuFrame = Toplevel()
    MenuFrame.title("Menu")
    MenuFrame.geometry("1920x1080+0+0")  # window size and position
    MenuFrame.state("zoomed")

    # Initialize the order list
    order_list = []

    # Establish connection and cursor
    conn = sqlite3.connect("db_member.db")
    cursor = conn.cursor()

    # Fetch food items from the database
    cursor.execute("SELECT food_name, description, price, food_category, Image_Path FROM food")
    menu_items = cursor.fetchall()

    # Create dictionaries for prices, images, and categories
    prices = {item[0]: item[2] for item in menu_items}  # Assuming item[0] is food_name and item[2] is price
    images = {}
    categories = {item[0]: item[3] for item in menu_items}  # Assuming item[0] is food_name and item[3] is food_category

    for item in menu_items:
        try:
            images[item[0]] = ImageTk.PhotoImage(Image.open(item[4]).resize((500, 550)))
        except Exception as e:
            print(f"Error loading image {item[4]}: {e}")

    # Global variable to store last order remark
    global last_order_remark
    last_order_remark = ""

    def ORDER_ID():
        return "".join(random.choices([str(i) for i in range(10)], k=6))

    def update_order_display():
        order_text = ""
        total = 0
        for item in order_list:
            order_text += f"{item['name']}....RM {item['price']}\n"
            total += item['price']
        orderTransaction.configure(text=order_text.strip())
        orderTotalLabel.configure(text=f"TOTAL : RM{total}")

    def add():
        dish_name = displayLabel.cget("text")
        order_list.append({"name": dish_name, "price": prices[dish_name]})
        update_order_display()

    def remove():
        dish_name = displayLabel.cget("text")
        for item in order_list:
            if item["name"] == dish_name:
                order_list.remove(item)
                break
        update_order_display()

    def display_dish(dish_name):
        for frame in dish_frames.values():
            frame.configure(style="DishFrame.TFrame")

        dish_frames[dish_name].configure(relief="sunken", style="SelectedDish.TFrame")
        displayLabel.configure(
            image=images[dish_name],
            text=dish_name,
            font=('Helvetica', 14, "bold"),
            foreground="white",
            compound="bottom",
            padding=(5, 5, 5, 5),
        )

    def order():
        global last_order_remark
        new_receipt = orderIDLabel.cget("text").replace("ORDER ID: ", "")
        order_day = date.today().isoformat()  # Convert date to ISO 8601 format
        order_total = sum(item['price'] for item in order_list)
        order_remark = remark.get()

        # Insert into Orders table
        cursor.execute("INSERT INTO Orders (order_date, order_total, remark) VALUES (?, ?, ?)",
                       (order_day, order_total, order_remark))
        order_id = cursor.lastrowid  # Get the last inserted order_id

        # Insert into OrderDetails table
        for item in order_list:
            cursor.execute("INSERT INTO OrderDetails (order_id, food_name, price) VALUES (?, ?, ?)",
                           (order_id, item['name'], item['price']))

        conn.commit()

        with open(new_receipt, 'w') as file:
            file.write("BlueDay\n")
            file.write("____________________\n")
            file.write(order_day + "\n")
            file.write("\n\n")
            for item in order_list:
                file.write(f"{item['name']}..RM {item['price']}\n")
            file.write("\n\n")
            file.write(f"TOTAL: RM{order_total}")

        # Update global variable with last order remark
        last_order_remark = order_remark

        orderTotalLabel.configure(text="TOTAL : RM0")
        orderIDLabel.configure(text="ORDER ID: " + ORDER_ID())
        orderTransaction.configure(text="")
        order_list.clear()
        remark.delete(0, 'end')  # Clear the remark Entry widget after submitting order

        messagebox.showinfo("Submit Order", "Your orders is submitted and preparing!")

    def view_order():
        view_order_window = Toplevel(MenuFrame)
        view_order_window.title("Order History")
        view_order_window.geometry("600x400")

        Label(view_order_window, text="Your Order History", font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Fetch the last order from Orders table
        cursor.execute("SELECT order_id, order_date, order_total, remark FROM Orders ORDER BY order_id DESC LIMIT 1")
        last_order = cursor.fetchone()

        if last_order:
            order_id = last_order[0]
            order_date = last_order[1]
            order_total = last_order[2]
            order_remark = last_order[3]

            # Display order ID and date
            Label(view_order_window, text=f"Order ID: {order_id}", font=('Helvetica', 12, 'bold')).pack(pady=5)
            Label(view_order_window, text=f"Date: {order_date}", font=('Helvetica', 12, 'bold')).pack(pady=5)

            # Display each food item in the order
            cursor.execute("SELECT food_name, price FROM OrderDetails WHERE order_id=?", (order_id,))
            order_details = cursor.fetchall()
            for detail in order_details:
                food_name = detail[0]
                price = detail[1]
                Label(view_order_window, text=f"{food_name} .... RM {price}", font=('Helvetica', 12)).pack(padx=20, pady=2)

            # Display remark for the order
            Label(view_order_window, text=f"Remark: {order_remark}", font=('Helvetica', 12, 'bold')).pack(pady=5)

            # Display total amount for the order
            Label(view_order_window, text=f"Total: RM {order_total}", font=('Helvetica', 12, 'bold')).pack(pady=10)
        else:
            # Display a message if there are no orders yet
            Label(view_order_window, text="No orders yet.", font=('Helvetica', 12)).pack(pady=10)

        btn_payment = Button(view_order_window, text="Pay at counter", width=20, command=payment, bg='blue',
                             fg='black', relief='raised')
        btn_payment.bind("<Enter>", lambda e: btn_payment.config(bg="lightblue"))
        btn_payment.bind("<Leave>", lambda e: btn_payment.config(bg="blue"))
        btn_payment.pack(pady=20)

    def payment():
        # Fetch necessary information for payment
        order_id = cursor.execute("SELECT order_id FROM Orders ORDER BY order_id DESC LIMIT 1").fetchone()[0]
        payment_date = date.today().isoformat()  # Assuming payment date is current date
        total_price = cursor.execute("SELECT order_total FROM Orders ORDER BY order_id DESC LIMIT 1").fetchone()[0]

        # Insert into Payment table
        cursor.execute("INSERT INTO Payment (order_id, Payment_Date, Total_price) VALUES (?, ?, ?)",
                       (order_id, payment_date, total_price))
        conn.commit()

        # Display a confirmation message to the user
        messagebox.showinfo("Payment Completed", "Payment has been successfully recorded.")

        # Example of further actions after payment (e.g., returning to home page)
        MenuFrame.destroy()
        MenuHomePage()

    # Styling and Images
    s = ttk.Style()
    s.configure('MainFrame.TFrame', background="#SlateGray")
    s.configure('MenuFrame.TFrame', background="LightCyan")
    s.configure('DisplayFrame.TFrame', background="#4A4A48")
    s.configure('OrderFrame.TFrame', background="lightslategray")
    s.configure('DishFrame.TFrame', background="LightCyan", relief="raised")
    s.configure('SelectedDish.TFrame', background="Black")
    s.configure('MenuLabel.TLabel', background="white", font=("Arial", 13, "italic"), foreground="black",
                padding=(5, 5, 5, 5), width=30)
    s.configure('orderTotalLabel.TLabel', background="black", font=("Arial", 10, "bold"), foreground="black",
                padding=(2, 2, 2, 2), anchor="w")
    s.configure('orderTransaction.TLabel', background="#4A4A48", font=('Helvetica', 12), foreground="black",
                wraplength=50, anchor="nw", padding=(3, 3, 3, 3))

    # Top Banner images
    TopBannerImageObject = Image.open(r"C:/Kai Shuang/background33.jpg").resize((1520, 140))
    TopBannerImage = ImageTk.PhotoImage(TopBannerImageObject)

    # Default display image
    displayDefaultImageObject = Image.open("C:/Kai Shuang/display.Default.jpg").resize((500, 540))
    displayDefaultImage = ImageTk.PhotoImage(displayDefaultImageObject)


    # Widgets
    mainFrame = ttk.Frame(MenuFrame, width=800, height=580, style='MainFrame.TFrame')
    mainFrame.grid(row=0, column=0, sticky="NSEW")

    topBannerFrame = ttk.Frame(mainFrame)
    topBannerFrame.grid(row=0, column=0, sticky="NSEW", columnspan=3)

    # Create a Canvas for the menuFrame to allow scrolling
    canvas = tk.Canvas(mainFrame, bg="#4A4A48", highlightthickness=0)
    canvas.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW")

    # Add a Scrollbar to the Canvas
    scrollbar = ttk.Scrollbar(mainFrame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=1, column=1, sticky="NSW")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create menuFrame inside the canvas
    menuFrame = ttk.Frame(canvas, style='MenuFrame.TFrame')
    menuWindow = canvas.create_window((0, 0), window=menuFrame, anchor="nw")

    # Ensure canvas resizes and updates its scroll region when menuFrame changes size
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    menuFrame.bind("<Configure>", on_frame_configure)

    displayFrame = ttk.Frame(mainFrame, style="DisplayFrame.TFrame")
    displayFrame.grid(row=1, column=1, padx=50, pady=10, sticky="NSEW")

    orderFrame = ttk.Frame(mainFrame, style="OrderFrame.TFrame")
    orderFrame.grid(row=1, column=2, padx=10, pady=10, sticky="NSEW")

    dish_frames = {}

    RestaurantBannerLabel = ttk.Label(topBannerFrame, image=TopBannerImage, background="#0F1110")
    RestaurantBannerLabel.grid(row=0, column=1, sticky="NSEW")

    MainMenuLabel = ttk.Label(menuFrame, text="MENU", style="MenuLabel.TLabel")
    MainMenuLabel.grid(row=0, column=0, sticky="WE")
    MainMenuLabel.configure(anchor="center", font=("Helvetica", 14, "bold"))

    # Group items by category
    category_items = {}
    for food_name, price in prices.items():
        category = categories[food_name]
        if category not in category_items:
            category_items[category] = []
        category_items[category].append((food_name, price))

    row = 1
    for category, items in category_items.items():
        category_label = ttk.Label(menuFrame, text=category, style="MenuLabel.TLabel", background='teal')
        category_label.grid(row=row, column=0, sticky="WE")
        row += 1
        for food_name, price in items:
            frame = ttk.Frame(menuFrame, style="DishFrame.TFrame")
            frame.grid(row=row, column=0, sticky="NSEW")
            label = ttk.Label(frame, text=f"{food_name} ..... RM{price}", style="MenuLabel.TLabel")
            label.grid(row=0, column=0, padx=10, pady=10, sticky="W")
            button = ttk.Button(frame, text="Display", command=lambda name=food_name: display_dish(name))
            button.grid(row=0, column=1, padx=10)
            dish_frames[food_name] = frame
            row += 1

    displayLabel = ttk.Label(displayFrame, image=displayDefaultImage, text="Welcome to Blueday",
                             font=('Helvetica', 14, "bold"), foreground="black", compound="bottom",
                             padding=(5, 5, 5, 5))
    displayLabel.grid(row=0, column=0, padx=(20, 5), pady=5, sticky="ns")

    displayFrame.grid_rowconfigure(0, weight=1)
    displayFrame.grid_columnconfigure(0, weight=1)

    AddDishButton = ttk.Button(displayFrame, text="Add to Order", command=add)
    AddDishButton.grid(row=1, column=0, pady=10, sticky="ew")

    RemoveDishButton = ttk.Button(displayFrame, text="Remove", command=remove)
    RemoveDishButton.grid(row=1, column=1, pady=10, sticky="ew")

    orderIDLabel = ttk.Label(orderFrame, text="ORDER ID: " + ORDER_ID(), style="orderTotalLabel.TLabel", background='#B7C4CF')
    orderIDLabel.grid(row=0, column=0, pady=5, sticky="WE")
    orderTransaction = ttk.Label(orderFrame, text="",font=('Arial', 7), style="orderTransaction.TLabel", background='#B7C4CF')
    orderTransaction.grid(row=1, column=0, pady=5, sticky="NSEW")
    orderTotalLabel = ttk.Label(orderFrame, text="TOTAL : RM0", style="orderTotalLabel.TLabel", background='#B7C4CF')
    orderTotalLabel.grid(row=2, column=0, pady=5, sticky="WE")

    lbl_remark = Label(orderFrame, text="Remark:", font=('Gill Sans Ultra Bold', 14), bd=12, bg='lightslategray')
    lbl_remark.grid(row=3, column=0)
    remark = Entry(orderFrame, font=('times new roman', 16), bd=18, bg='grey')
    remark.grid(row=4, column=0, padx=30, pady=20)

    OrderButton = ttk.Button(orderFrame, text="Complete Order", command=order)
    OrderButton.grid(row=5, column=0, pady=10)

    btn_orderhistory = ttk.Button(orderFrame, text="View My Order", command=view_order)
    btn_orderhistory.grid(row=6, column=0, pady=10)


def Exit():
    result = messagebox.askquestion('System', 'Are you sure you want to exit?', icon="warning")
    if result == 'yes':
        root.destroy()


def Pickup_or_Dinein_window():
    global PODFrame
    PODFrame = Frame(root)
    root.withdraw()
    PODFrame = Toplevel()
    PODFrame.title("Pick Up OR Dine In")
    PODFrame.geometry("1920x1080+0+0")

    image = Image.open("C:/Kai Shuang/wallpaper2.jpg")  # Replace with your image file path
    resized_image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    bg_label = Label(PODFrame, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    lbl_POD = Label(PODFrame, text="Select your Dining options", font=('Gill Sans Ultra Bold', 30, 'bold'))
    lbl_POD.pack(pady=100)

    btn_pickup = Button(PODFrame, text="Pick Up", font=('times new roman', 16), width=20, command=MenuHomePage,bd=18, bg='darksalmon',
                        fg='black', relief='raised')
    btn_pickup.bind("<Enter>", lambda e: btn_pickup.config(bg="salmon"))
    btn_pickup.bind("<Leave>", lambda e: btn_pickup.config(bg="darksalmon"))
    btn_pickup.pack(pady=20)

    btn_dinein = Button(PODFrame, text="Dine In", font=('times new roman', 16), width=20, command=MenuHomePage,bd=18, bg='darksalmon',
                        fg='black', relief='raised')
    btn_dinein.bind("<Enter>", lambda e: btn_dinein.config(bg="salmon"))
    btn_dinein.bind("<Leave>", lambda e: btn_dinein.config(bg="darksalmon"))
    btn_dinein.pack(pady=20)

    # Keep a reference to the image object to prevent garbage collection
    PODFrame.image = bg_image


def Home():
    global HomeFrame
    for widget in root.winfo_children():
        widget.destroy()

    HomeFrame = Frame(root)
    HomeFrame.pack(side='left', pady=60)
    root.withdraw()  # Hide the main login window
    HomeFrame = Toplevel()  # Create a new window
    HomeFrame.title("Home")
    HomeFrame.geometry('1920x1080+0+0')

    # Load the background image
    image = Image.open("C:/Kai Shuang/wallpaper.jpg")  # Replace with your image file path
    resized_image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    bg_label = Label(HomeFrame, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    lbl_home = Label(HomeFrame, text="Welcome To Work", font=('Gill Sans Ultra Bold', 40, 'bold'),bg="navajowhite")
    lbl_home.pack(pady=100)

    btn_dashboard = Button(HomeFrame, text="Edit Menu", font=('times new roman', 16), width=20, command=EditMenu,
                           bg='darkgray',bd=18,
                           fg='black', relief='raised')
    btn_dashboard.bind("<Enter>", lambda e: btn_dashboard.config(bg="lightblue"))
    btn_dashboard.bind("<Leave>", lambda e: btn_dashboard.config(bg="darkgray"))
    btn_dashboard.pack(pady=20)

    btn_viewcustomerorder = Button(HomeFrame, text="View Customer Order", font=('times new roman', 16), width=20, command=viewcustomerorder,
                           bg='darkgray',bd=18,
                           fg='black', relief='raised')
    btn_viewcustomerorder.bind("<Enter>", lambda e: btn_viewcustomerorder.config(bg="lightblue"))
    btn_viewcustomerorder.bind("<Leave>", lambda e: btn_viewcustomerorder.config(bg="darkgray"))
    btn_viewcustomerorder.pack(pady=20)

    btn_reviewreport = Button(HomeFrame, text="Rating and Review Report", font=('times new roman', 16), width=20,
                              command=open_report_window,bd=18, bg='darkgray',
                              fg='black', relief='raised')
    btn_reviewreport.bind("<Enter>", lambda e: btn_reviewreport.config(bg="lightblue"))
    btn_reviewreport.bind("<Leave>", lambda e: btn_reviewreport.config(bg="darkgray"))
    btn_reviewreport.pack(pady=20)

    btn_logout = Button(HomeFrame, text="Logout", font=('times new roman', 16), width=20, command=Logout1,bd=18, bg='darkgray',
                        fg='black',
                        relief='raised')
    btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg="lightblue"))
    btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg="darkgray"))
    btn_logout.pack(pady=20)

    # Keep a reference to the image object to prevent garbage collection
    HomeFrame.image = bg_image

current_rating = 0
reviews = []

def viewcustomerorder():
    global customerFrame
    for widget in root.winfo_children():
        widget.destroy()

    customerFrame = Frame(root)
    customerFrame.pack(side='left', fill="both", pady=200)
    root.withdraw()  # Hide the main login window
    customerFrame = Toplevel()  # Create a new window
    customerFrame.title("Customer Order")
    customerFrame.geometry('1920x1080+0+0')
    customerFrame.state('zoomed')

    # Load the background image
    image = Image.open("C:/Kai Shuang/wallpaper4.jpg")  # Replace with your image file path
    resized_image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    bg_label = Label(customerFrame, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def fetch_orders(date=None):
        conn = sqlite3.connect("db_member.db")
        cursor = conn.cursor()

        query = "SELECT Orders.order_id, Orders.order_date, Orders.remark, Orders.order_total, \
                        OrderDetails.food_name, OrderDetails.price \
                        FROM Orders \
                        INNER JOIN OrderDetails ON Orders.order_id = OrderDetails.order_id"

        if date:
            query += " WHERE Orders.order_date LIKE ?"
            cursor.execute(query, (date + '%',))
        else:
            cursor.execute(query)

        orders = cursor.fetchall()
        conn.close()
        return orders

    def update_order_list(date=None):
        for row in order_list.get_children():
            order_list.delete(row)

        orders = fetch_orders(date)

        if not orders:
            order_list.insert("", "end", text="", values=("", "", "", ""), tags=("no_orders",))
            order_list.tag_configure("no_orders", background="red")
            order_list.insert("", "end", text="No orders found for {}".format(date if date else "all dates"))
        else:
            for order in orders:
                food_name = order[4]
                order_id = order[0]
                order_date = order[1]
                remark = order[2]
                total = order[3]

                order_list.insert("", "end", text=food_name, values=(order_id, order_date, remark, total))

    # Create a table or list to display orders
    order_list = ttk.Treeview(customerFrame, columns=("Order ID", "Order Date", "Remark", "Total"))
    order_list.heading("#0", text="Food Name")
    order_list.heading("Order ID", text="Order ID")
    order_list.heading("Order Date", text="Order Date")
    order_list.heading("Remark", text="Remark")
    order_list.heading("Total", text="Total")

    order_list.pack(expand=True, padx=20, pady=200, fill="both")

    Label(customerFrame, text="Select Date:",font=('times new roman', 16)).place(x=700,y=100),
    cal = DateEntry(customerFrame, width=12, background='darkblue', foreground='white', borderwidth=2, year=2024,
                    month=7, day=3, date_pattern='y-mm-dd')
    cal.place(x=705,y=150)

    def on_date_select(event):
        selected_date = cal.get()
        update_order_list(selected_date)

    cal.bind("<<DateEntrySelected>>", on_date_select)

    btn_logout = Button(customerFrame, text="Logout", font=('times new roman', 16), width=15, bd=12,
                        command=Logout4, bg='red', fg='black', relief='raised')
    btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg="pink"))
    btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg="red"))
    btn_logout.place(x=1300, y=730)

    update_order_list()  # Display all orders initially

    # Keep a reference to the image object to prevent garbage collection
    customerFrame.image = bg_image

# Function to handle star click
def set_rating(rating):
    global current_rating
    current_rating = rating
    update_stars()


# Function to update star display
def update_stars():
    global stars
    for i in range(5):
        if i < current_rating:
            stars[i].config(text='★', fg='gold')
        else:
            stars[i].config(text='☆', fg='gray')


# Function to handle review submission
def submit_review():
    review_text = review_entry.get("1.0", "end-1c").strip()
    email = email_entry.get().strip()
    if not email:
        messagebox.showwarning("Missing Email", "Please enter your email.")
        return

    if 1 <= current_rating <= 5 and review_text:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        reviews.append((current_rating, review_text, email, timestamp))
        messagebox.showinfo("Review Submitted", "Thank you for your review!")
        clear_fields()
    else:
        messagebox.showwarning("Incomplete Review", "Please select a rating and enter your review.")


# Function to clear input fields after submission
def clear_fields():
    review_entry.delete("1.0", "end")
    email_entry.delete(0, "end")
    set_rating(0)


# Function to generate PDF report for a specific date and open it
def generate_pdf_report_for_date(date):
    filtered_reviews = [review for review in reviews if review[3].startswith(date)]

    if not filtered_reviews:
        messagebox.showwarning("No Reviews", f"No reviews found for {date}.")
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Customer Ratings and Reviews for {date}", ln=True, align='C')
    pdf.ln(10)

    col_widths = [40, 50, 85, 15]  # Widths for columns: Date/Time, Email, Rating, Review

    # Table header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_text_color(0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)  # Set line width for borders

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_widths[0], 10, "Date/Time", 1, 0, 'C', 1)
    pdf.cell(col_widths[1], 10, "Email", 1, 0, 'C', 1)
    pdf.cell(col_widths[2], 10, "Review", 1, 0, 'C', 1)  # '1' indicates end of line after cell
    pdf.cell(col_widths[3], 10, "Rating", 1, 1, 'C', 1)

    # Table rows
    pdf.set_font("Arial", size=12)
    for rating, review, email, timestamp in filtered_reviews:
        pdf.cell(col_widths[0], 10, timestamp, 1, 0, 'C')
        pdf.cell(col_widths[1], 10, email, 1, 0, 'C')
        pdf.cell(col_widths[2], 10, review, 1, 0, 'L')  # '1' indicates end of line after multi_cell
        pdf.cell(col_widths[3], 10, str(rating), 1, 1, 'C')

    # Save PDF file
    pdf_file = f"customer_reviews_{date}.pdf"
    pdf.output(pdf_file)
    messagebox.showinfo("PDF Saved", f"Reviews have been saved to {pdf_file}")

    # Open the PDF file after saving
    try:
        subprocess.Popen([pdf_file], shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open PDF: {e}")


# Function to view reviews for a specific date
def view_reviews():
    date = cal.get_date().strftime("%Y-%m-%d")
    review_list.delete(0, tk.END)
    filtered_reviews = [review for review in reviews if review[3].startswith(date)]

    if not filtered_reviews:
        review_list.insert(tk.END, f"No reviews found for {date}.")
    else:
        for rating, review, email, timestamp in filtered_reviews:
            review_list.insert(tk.END, f"{timestamp} - {email} - {rating}★\n{review}\n")


# Function to open the review report window
def open_report_window():
    report_window = tk.Toplevel(root)
    report_window.title("Review Report")
    report_window.geometry("1920x1080+0+0")

    # Load the background image
    image = Image.open("C:/Kai Shuang/background7.jpg")  # Replace with your image file path
    resized_image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    bg_label = Label(report_window, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    report_name = Label(report_window, text="Rating and Review Report", font=('Eras Bold ITC', 25), bg='lightpink')
    report_name.pack(pady=70)

    tk.Label(report_window, text="Select Date:", font=('Cascadia Code', 16),bg='lightpink').pack(pady=5)

    #Create Calendar Table
    global cal
    cal = DateEntry(report_window, width=12, background='darkblue', foreground='white', borderwidth=2)
    cal.pack(pady=5)

    tk.Button(report_window, text="View Reviews", font=("Arial", 10), command=view_reviews).pack(pady=5)

    global review_list
    review_list = tk.Listbox(report_window, width=80, height=20)
    review_list.pack(pady=5)

    tk.Button(report_window, text="Download PDF", font=("Arial", 10),
              command=lambda: generate_pdf_report_for_date(cal.get_date().strftime("%Y-%m-%d"))).pack(pady=5)

    # Keep a reference to the image object to prevent garbage collection
    report_window.image = bg_image


def Ratingwindow():
    global review_entry, email_entry, stars

    root = tk.Tk()
    root.title("Customer Rating and Review")
    root.config(bg="#B7C4CF")

    stars_frame = tk.Frame(root)
    stars_frame.grid(row=1, column=0, columnspan=5)
    stars_frame.config(bg="#B7C4CF")


    # Rating stars
    stars = []
    for i in range(5):
        star = tk.Label(stars_frame, text='☆', font=("Arial", 25), fg='gray',bg="#B7C4CF")
        star.grid(row=0, column=i, padx=5)
        star.bind("<Button-1>", lambda e, i=i + 1: set_rating(i))
        stars.append(star)

    # Frame for review entry
    review_frame = tk.Frame(root)
    review_frame.grid(row=2, column=0, columnspan=5)
    review_frame.config(bg="#B7C4CF")

    # Review label and entry
    review_label = tk.Label(review_frame, text="Review:", font=('Cascadia Code', 16),bg="#B7C4CF")
    review_label.grid(row=0, column=0, pady=10)

    global review_entry
    review_entry = tk.Text(review_frame, height=5, width=40)
    review_entry.grid(row=0, column=1, padx=5)

    # Frame for email entry
    email_frame = tk.Frame(root)
    email_frame.grid(row=0, column=0, columnspan=5)
    email_frame.config(bg="#B7C4CF")

    # Email label and entry
    email_label = tk.Label(email_frame, text="Email:", font=('Cascadia Code', 16),bg="#B7C4CF")
    email_label.grid(row=0, column=0, pady=10)

    global email_entry
    email_entry = tk.Entry(email_frame, width=40)
    email_entry.grid(row=0, column=1, padx=5)

    # Frame for buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=3, column=0, columnspan=5)
    button_frame.config(bg="#B7C4CF")

    # Submit button
    submit_button = tk.Button(button_frame, text="Submit", font=('Cascadia Code', 12),bd=10, command=submit_review,bg="lightsalmon")
    submit_button.grid(row=0, column=0, padx=5, pady=10)


def add_food_window():
    # Create a new window for adding food
    add_food_window = Toplevel()
    add_food_window.title("Add Food")
    add_food_window.grid_columnconfigure(0, weight=1)
    add_food_window.grid_columnconfigure(1, weight=1)
    add_food_window.config(bg='lightpink')
    add_food_window.geometry("1920x1080+0+0")

    # Define the layout of the window
    label_food_name = Label(add_food_window, text="Food Name:", font=('Eras Bold ITC', 14), bg='lightpink')
    label_food_name.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_food_name = Entry(add_food_window, font=('times new roman', 16))
    entry_food_name.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    label_description = Label(add_food_window, text="Description:", font=('Eras Bold ITC', 14), bg='lightpink')
    label_description.grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_description = Entry(add_food_window, font=('times new roman', 16))
    entry_description.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    label_price = Label(add_food_window, text="Price:", font=('Eras Bold ITC', 14), bg='lightpink')
    label_price.grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_price = Entry(add_food_window, font=('times new roman', 16))
    entry_price.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    label_food_category = Label(add_food_window, text="Food Category:", font=('Eras Bold ITC', 14), bg='lightpink')
    label_food_category.grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_food_category = Entry(add_food_window, font=('times new roman', 16))
    entry_food_category.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    label_Image_Path = Label(add_food_window, text="Image Path:", font=('Eras Bold ITC', 14), bg='lightpink')
    label_Image_Path.grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_Image_Path = Entry(add_food_window, font=('times new roman', 16))
    entry_Image_Path.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    image_label = Label(add_food_window)
    image_label.grid(row=0,column=2,rowspan=6,padx=10,pady=10)


    # Create a button to add the food
    btn_add_food = Button(add_food_window, text="Add Food", font=('Eras Bold ITC', 14), border=7,
                          command=lambda:[add_food(entry_food_name, entry_description, entry_price, entry_food_category, entry_Image_Path),add_food_window.destroy()])
    btn_add_food.grid(row=5, columnspan=2, pady=10)
    btn_add_food.config(bg='lightsalmon')
    btn_select_food = Button(add_food_window, text="Select Food", font=('Eras Bold ITC', 14), border=7, command=lambda:photoinsert(entry_Image_Path,image_label))
    btn_select_food.grid(row=6, columnspan=2, pady=10)
    btn_select_food.config(bg='lightsalmon')
    btn_back = Button(add_food_window, text="Back to Dashboard", font=('Eras Bold ITC', 14), border=7,
                      command=EditMenu)
    btn_back.grid(row=7, columnspan=2, pady=10)
    btn_back.config(bg='lightsalmon')


def add_food(entry_food_name, entry_description, entry_price, entry_food_category, entry_Image_Path,):
    # Get the values entered by the user
    food_name = entry_food_name.get()
    description = entry_description.get()
    price = entry_price.get()
    food_category = entry_food_category.get()
    Image_Path = entry_Image_Path.get()

    # Check if all fields are filled
    if food_name and description and price and food_category and Image_Path:
        try:
            # Insert the food details into the database
            cursor.execute("INSERT INTO food (food_name, description, price, food_category, Image_Path) VALUES (?, ?, ?, ?, ?)",
                           (food_name, description, price, food_category, Image_Path))
            conn.commit()  # Commit the transaction
            messagebox.showinfo("Success", "Food successfully added!")

            # Fetch data from the database and update the food_treeview
            update_food_treeview()


        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error adding food: {e}")
    else:
        messagebox.showerror("Error", "Please fill in all fields!")


def update_food_treeview():
    # Clear existing data in the treeview
    for item in food_treeview.get_children():
        food_treeview.delete(item)

    try:
        # Fetch data from the database
        cursor.execute("SELECT food_name, description, price , food_category, Image_Path FROM food")
        rows = cursor.fetchall()

        # Populate the treeview with fetched data
        for row in rows:
            food_treeview.insert("", "end", values=row)
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error fetching food data: {e}")


def EditMenu():
    global FoodFrame, food_treeview
    for widget in root.winfo_children():
        widget.destroy()

    def selectpic(event):
        select_food = food_treeview.selection()
        if select_food:
            item = food_treeview.item(select_food)
            Image_path = item['value'][5]
            food_name = item['value'][1]

            try:
                image = Image.open(Image_path)
                width, height = image.size

                if width > height:
                    left = (width - height) / 2
                    top = 0
                    right = (width + height) / 2
                    bottom = height

                else:
                    left = 0
                    top = (height - width) / 2
                    right = width
                    bottom = (height + width) / 2

                image = image.crop((left, top, right, bottom))

                image.thumbnail((400, 400), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(image)

                image_label.config(image=photo)
                image_label.image = photo

            except Exception as e:
                messagebox.showerror("Error", f"Error loading image:{e}")

    FoodFrame = Toplevel()
    FoodFrame.title("Edit Menu")
    FoodFrame.geometry("1920x1080+0+0")  # window size and position
    FoodFrame.state("zoomed")

    # Load the background image
    image = Image.open("C:/Kai Shuang/wallpaper3.jpg")  # Replace with your image file path
    resized_image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    bg_label = Label(FoodFrame, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=('times new roman', 14), foreground="Green")

    food_treeview = ttk.Treeview(FoodFrame, columns=("Food Name", "Description", "Price", "Food Category", "Image Path"),
                                 show='headings', height=20, style="Treeview")



    # Create the food options buttons
    btn_add_food = Button(FoodFrame, text="Add Food", font=('times new roman', 16), width=15,bd=12,
                          command=add_food_window, bg='darksalmon', fg='black', relief='raised')
    btn_add_food.bind("<Enter>", lambda e: btn_add_food.config(bg="salmon"))
    btn_add_food.bind("<Leave>", lambda e: btn_add_food.config(bg="darksalmon"))
    btn_add_food.pack(side="top", pady=10, padx=80)


    btn_delete_food = Button(FoodFrame, text="Delete Food", font=('times new roman', 16), width=15,bd=12,
                             command=delete_food, bg='pink', fg='black', relief='raised')
    btn_delete_food.bind("<Enter>", lambda e: btn_delete_food.config(bg="lightpink"))
    btn_delete_food.bind("<Leave>", lambda e: btn_delete_food.config(bg="pink"))
    btn_delete_food.pack(side="top",pady=10, padx=80)

    btn_update_food = Button(FoodFrame, text="Update Food", font=('times new roman', 16), width=15,bd=12,
                             command=update_food_window, bg='mediumpurple', fg='black', relief='raised')
    btn_update_food.bind("<Enter>", lambda e: btn_update_food.config(bg="lightblue"))
    btn_update_food.bind("<Leave>", lambda e: btn_update_food.config(bg="mediumpurple"))
    btn_update_food.pack(side="top", pady=10, padx=80)


    food_treeview.bind("<<TreeviewSelect>>", selectpic)

    # Create a Treeview widget to display food items
    food_treeview = ttk.Treeview(FoodFrame, columns=("Food Name", "Description", "Price", "Food Category", "Image Path"),
                                 show='headings', height=20)
    food_treeview.heading("Food Name", text="Food Name")
    food_treeview.heading("Description", text="Description")
    food_treeview.heading("Price", text="Price")
    food_treeview.heading("Food Category", text="Food Category")
    food_treeview.heading("Image Path", text="Image Path")

    food_treeview.column("Food Name", width=150, anchor="center")
    food_treeview.column("Description", width=150, anchor="center")
    food_treeview.column("Price", width=150, anchor="center")
    food_treeview.column("Food Category", width=150, anchor="center")
    food_treeview.column("Image Path", width=150, anchor="center")
    food_treeview.pack(fill="both", pady=60, padx=60)

    btn_logout = Button(FoodFrame, text="Logout", font=('times new roman', 16), width=15,bd=12,
                        command=Logout2, bg='red', fg='black', relief='raised')
    btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg="pink"))
    btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg="red"))
    btn_logout.place(x=1300, y=730)

    # Populate the treeview with food data from the database
    update_food_treeview()

    # Keep a reference to the image object to prevent garbage collection
    FoodFrame.image = bg_image


def update_food_window():
    # Get the selected food_id
    food_id = get_selected_food_id()

    if food_id:
        try:
            # Fetch the selected food details from the database
            cursor.execute("SELECT food_name, description, price, food_category, Image_Path FROM food WHERE food_id=?", (food_id,))
            food_details = cursor.fetchone()
            if food_details:
                # Create a new window for updating food
                update_food_window = Toplevel()
                update_food_window.title("Update Food")
                update_food_window.config(bg="blueviolet")
                update_food_window.geometry("1920x1080+0+0")

                # Define the layout of the window
                label_food_name = Label(update_food_window, text="Food Name:", font=('times new roman', 16),bg="blueviolet")
                label_food_name.grid(row=0, column=0, padx=10, pady=10, sticky="e")
                entry_food_name = Entry(update_food_window, font=('times new roman', 16))
                entry_food_name.grid(row=0, column=1, padx=10, pady=10, sticky="w")
                entry_food_name.insert(0, food_details[0])  # Food name

                label_description = Label(update_food_window, text="Description:", font=('times new roman', 16),bg="blueviolet")
                label_description.grid(row=1, column=0, padx=10, pady=10, sticky="e")
                entry_description = Entry(update_food_window, font=('times new roman', 16))
                entry_description.grid(row=1, column=1, padx=10, pady=10, sticky="w")
                entry_description.insert(0, food_details[1])  # Description

                label_price = Label(update_food_window, text="Price:", font=('times new roman', 16),bg="blueviolet")
                label_price.grid(row=2, column=0, padx=10, pady=10, sticky="e")
                entry_price = Entry(update_food_window, font=('times new roman', 16))
                entry_price.grid(row=2, column=1, padx=10, pady=10, sticky="w")
                entry_price.insert(0, food_details[2])  # Price

                label_food_category = Label(update_food_window, text="Food Category:", font=('times new roman', 16),bg="blueviolet")
                label_food_category.grid(row=3, column=0, padx=10, pady=10, sticky="e")
                entry_food_category = Entry(update_food_window, font=('times new roman', 16))
                entry_food_category.grid(row=3, column=1, padx=10, pady=10, sticky="w")
                entry_food_category.insert(0, food_details[3])  # Food Category


                label_Image_Path = Label(update_food_window, text="Image Path:", font=('Eras Bold ITC', 14),
                                         bg='blueviolet')
                label_Image_Path.grid(row=4, column=0, padx=10, pady=10, sticky="e")
                entry_Image_Path = Entry(update_food_window, font=('times new roman', 16))
                entry_Image_Path.grid(row=4, column=1, padx=10, pady=10, sticky="w")

                image_label = Label(update_food_window)
                image_label.grid(row=0, column=2, rowspan=6, padx=10, pady=10)


                btn_select_food = Button(update_food_window, text="Select Food", font=('Eras Bold ITC', 14), border=7,
                                         command=lambda: photoinsert(entry_Image_Path, image_label))
                btn_select_food.grid(row=6, columnspan=2, pady=10)
                btn_select_food.config(bg='mediumpurple')

                btn_back = Button(update_food_window, text="Back to Dashboard", font=('Eras Bold ITC', 14), border=7,
                                  command=EditMenu)
                btn_back.grid(row=7, columnspan=2, pady=10)
                btn_back.config(bg='mediumpurple')

                # Create a button to update the food
                btn_update_food = Button(update_food_window, text="Update Food", font=('Eras Bold ITC', 14), border=7, bg='mediumpurple',
                                         command=lambda: [update_food(food_id, entry_food_name.get(), entry_description.get(), entry_price.get(), entry_food_category.get(), entry_Image_Path.get()),update_food_window.destroy()])
                btn_update_food.grid(row=5, columnspan=2, pady=20)
            else:
                messagebox.showerror("Error", "Selected food details not found.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching food details: {e}")

def photoinsert(entry_Image_Path,image_label):
    file = filedialog.askopenfilename(filetypes=[("Image files","*.jpg *.jpeg *.png *.gif")])
    if file:
        entry_Image_Path.delete(0, END)
        entry_Image_Path.insert(0, file)

        try:
            image = Image.open(file)
            width, height = image.size

            if width > height:
                left = (width - height) / 2
                top = 0
                right = (width + height) / 2
                bottom = height

            else:
                left = 0
                top = (height - width) / 2
                right = width
                bottom = (height + width) / 2

            image = image.crop ((left, top, right, bottom)).resize((400,400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo

        except Exception as e:
            messagebox.showerror("Error",f"Error loading image:{e}")

def get_selected_food_id():
    selected_item = food_treeview.selection()
    if selected_item:
        item_values = food_treeview.item(selected_item, 'values')
        cursor.execute("SELECT food_id FROM food WHERE food_name=?", (item_values[0],))
        food_id = cursor.fetchone()
        if food_id:
            return food_id[0]  # Return the food id
        else:
            messagebox.showerror("Error", "Selected food id not found.")
    else:
        messagebox.showerror("Error", "Please select a food item.")


def update_food(food_id, food_name, description, price, food_category, Image_Path):
    try:
        cursor.execute("UPDATE food SET food_name=?, description=?, price=?, food_category=?, Image_Path=? WHERE food_id=?",
                       (food_name, description, price, food_category, Image_Path, food_id))
        conn.commit()  # Commit the transaction
        messagebox.showinfo("Success", "Food details updated successfully!")

        # Fetch the updated data from the database and update the food treeview
        update_food_treeview()

        # Show the food dashboard
        EditMenu()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error updating food details: {e}")


def delete_food():
    # Get the selected item from the Treeview
    selected_item = food_treeview.selection()

    if not selected_item:
        messagebox.showerror("Error", "Please select a food item to delete.")
        return

    # Get the item's values
    item_values = food_treeview.item(selected_item, 'values')
    food_name = item_values[0]

    # Prompt the user for confirmation
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{food_name}'?")

    if confirm:
        try:
            # Delete the selected item from the database table
            cursor.execute("DELETE FROM food WHERE food_name=?", (food_name,))  # cursor is SQL language
            conn.commit()  # Commit the transaction

            # Delete the selected item from the Treeview
            food_treeview.delete(selected_item)
            messagebox.showinfo("Success", f"'{food_name}' deleted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error deleting food: {e}")


def MenuHomePage():
    global MenuHomePageFrame
    for widget in root.winfo_children():
        widget.destroy()
    MenuHomePageFrame = Frame(root)
    MenuHomePageFrame.pack(side='left', pady=60)
    MenuHomePageFrame = Toplevel()  # Create a new window
    MenuHomePageFrame.title("MenuHome")
    MenuHomePageFrame.geometry('1920x1080+0+0')

    image = Image.open("C:/Kai Shuang/wallpaper1.jpg")  # Replace with your image file path
    resized_image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    bg_label = Label(MenuHomePageFrame, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    lbl_menuhome = Label(MenuHomePageFrame, text="Welcome To Eat", font=('Gill Sans Ultra Bold', 40, 'bold'),bg='lightgoldenrodyellow')
    lbl_menuhome.pack(pady=100)

    btn_Menu = Button(MenuHomePageFrame, text="Menu", font=('times new roman', 16), width=20, command=Menu,bd=18, bg='darkgray',
                      fg='black', relief='raised')
    btn_Menu.bind("<Enter>", lambda e: btn_Menu.config(bg="lightblue"))
    btn_Menu.bind("<Leave>", lambda e: btn_Menu.config(bg="darkgray"))
    btn_Menu.pack(pady=20)

    btn_Ratingandreview = Button(MenuHomePageFrame, text="Give a Feedback", font=('times new roman', 16), width=20,
                                 command=Ratingwindow, bg='darkgray',bd=18,
                                 fg='black', relief='raised')
    btn_Ratingandreview.bind("<Enter>", lambda e: btn_Ratingandreview.config(bg="lightblue"))
    btn_Ratingandreview.bind("<Leave>", lambda e: btn_Ratingandreview.config(bg="darkgray"))
    btn_Ratingandreview.pack(pady=20)

    btn_logout = Button(MenuHomePageFrame, text="Logout", font=('times new roman', 16), width=20, command=Logout3,bd=18,
                        bg='darkgray',fg='black',relief='raised')
    btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg="lightblue"))
    btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg="darkgray"))
    btn_logout.pack(pady=20)

    # Keep a reference to the image object to prevent garbage collection
    MenuHomePageFrame.image = bg_image


def Logout1(event=None):
    global root
    root.deiconify()
    StaffLoginForm()
    HomeFrame.destroy()
    # Clear the username and password fields
    STAFF_LOGIN.set("")
    STAFF_PASSWORD_LOGIN.set("")

def Logout2(event=None):
    global root
    root.deiconify()
    Home()
    FoodFrame.destroy()

def Logout3(event=None):
    global root
    root.deiconify()
    LoginForm()
    MenuHomePageFrame.destroy()


    USERNAME_LOGIN.set("")
    PASSWORD_LOGIN.set("")

def Logout4(event=None):
    global root
    root.deiconify()
    Home()
    customerFrame.destroy()



def on_entry_click(event, entry, placeholder, var, is_password=False):
    """Function to handle when the entry widget is clicked."""
    if entry.get() == placeholder:
        var.set("")  # Clear the placeholder text
        entry.config(fg='black',
                     show='*' if is_password else '')  # Change text color to black and hide text if password


def on_focusout(event, entry, placeholder, var, is_password=False):
    """Function to handle when the entry widget loses focus."""
    if entry.get() == '':
        var.set(placeholder)  # Restore the placeholder text
        entry.config(fg='grey', show='' if is_password else '')  # Change text color to grey and show text if password


def LoginForm():
    global LoginFrame, lbl_result1
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg='dodgerblue')
    LoginFrame = tk.Frame(root)
    LoginFrame.pack(side='top', pady=200)
    LoginFrame.config(bg='lightsteelblue')


    lbl_title = tk.Label(LoginFrame, text="LogIn:", font=('times new roman', 20, 'bold'), bd=18, bg='lightsteelblue')
    lbl_title.grid(row=0, columnspan=3)

    lbl_username = tk.Label(LoginFrame, text="Username:", font=('times new roman', 16), bd=18, bg='lightsteelblue')
    lbl_username.grid(row=1, column=0)

    lbl_password = tk.Label(LoginFrame, text="Password:", font=('times new roman', 16), bd=18, bg='lightsteelblue')
    lbl_password.grid(row=2, column=0)

    USERNAME_LOGIN.set("Enter Your UserName")
    PASSWORD_LOGIN.set("Enter Your Password")

    username = tk.Entry(LoginFrame, font=('times new roman', 14), textvariable=USERNAME_LOGIN, width=20)
    username.config(fg='grey')
    username.grid(row=1, column=1, columnspan=2, padx=30)
    username.bind('<FocusIn>', lambda event: on_entry_click(event, username, "Enter Your UserName", USERNAME_LOGIN))
    username.bind('<FocusOut>', lambda event: on_focusout(event, username, "Enter Your UserName", USERNAME_LOGIN))

    password = tk.Entry(LoginFrame, font=('times new roman', 14), textvariable=PASSWORD_LOGIN, width=20)
    password.config(fg='grey', show='')
    password.grid(row=2, column=1, columnspan=2, padx=30)
    password.bind('<FocusIn>',
                  lambda event: on_entry_click(event, password, "Enter Your Password", PASSWORD_LOGIN, True))
    password.bind('<FocusOut>', lambda event: on_focusout(event, password, "Enter Your Password", PASSWORD_LOGIN, True))

    btn_login = tk.Button(LoginFrame, text="Login", font=('times new roman', 16), width=20, command=Login, bg='blue',
                          fg='white', relief='raised')
    btn_login.bind("<Enter>", lambda e: btn_login.config(bg="lightblue"))
    btn_login.bind("<Leave>", lambda e: btn_login.config(bg="blue"))
    btn_login.grid(row=4, columnspan=3, pady=30)

    lbl_text = tk.Label(LoginFrame, text="Not a member?", font=('times new roman', 14), bg='lightsteelblue')
    lbl_text.grid(row=5, columnspan=3)

    lbl_register = tk.Label(LoginFrame, text="Register Now", fg="Blue", font=('arial', 12), bg='lightsteelblue')
    lbl_register.bind('<Enter>', lambda event, label=lbl_register: label.config(font=('arial', 12, 'underline')))
    lbl_register.bind('<Leave>', lambda event, label=lbl_register: label.config(font=('arial', 12)))
    lbl_register.bind('<Button-1>', ToggleToRegister)
    lbl_register.grid(row=6, columnspan=3)

    lbl_home = tk.Label(LoginFrame, text="Home Page", fg="Blue", font=('arial', 12), bg='lightsteelblue')
    lbl_home.bind('<Enter>', lambda event, label=lbl_home: label.config(font=('arial', 12, 'underline')))
    lbl_home.bind('<Leave>', lambda event, label=lbl_home: label.config(font=('arial', 12)))
    lbl_home.bind('<Button-1>', lambda event: create_homepage())
    lbl_home.grid(row=7, columnspan=3)


def StaffLoginForm():
    global LoginFrame, lbl_result1
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg='rosybrown')
    LoginFrame = Frame(root)
    LoginFrame.pack(side='top', pady=200)
    LoginFrame.config(bg='peachpuff')

    lbl_title = Label(LoginFrame, text="Staff Login:", font=('times new roman', 20, 'bold'), bd=18, bg='peachpuff')
    lbl_title.grid(row=0, columnspan=3)

    lbl_Staff_name = Label(LoginFrame, text="Staff Name:", font=('times new roman', 16), bd=18, bg='peachpuff')
    lbl_Staff_name.grid(row=1, column=0)

    lbl_password = Label(LoginFrame, text="Password:", font=('times new roman', 16), bd=18, bg='peachpuff')
    lbl_password.grid(row=2, column=0)

    Staff_name = Entry(LoginFrame, font=('times new roman', 16), textvariable=STAFF_LOGIN, width=15)
    Staff_name.grid(row=1, column=1, columnspan=2, padx=30)

    password = Entry(LoginFrame, font=('times new roman', 16), textvariable=STAFF_PASSWORD_LOGIN, width=15, show="*")
    password.grid(row=2, column=1, columnspan=2, padx=30)

    btn_login = Button(LoginFrame, text="Login", font=('times new roman', 16), width=20, command=StaffLogin, bg='blue',
                       fg='white',
                       relief='raised')
    btn_login.bind("<Enter>", lambda e: btn_login.config(bg="lightblue"))
    btn_login.bind("<Leave>", lambda e: btn_login.config(bg="blue"))
    btn_login.grid(row=4, columnspan=3, pady=30)

    lbl_text = Label(LoginFrame, text="Not a staff?", font=('times new roman', 14), bg='peachpuff')
    lbl_text.grid(row=5, columnspan=3)

    lbl_register = Label(LoginFrame, text="Register Now", fg="Blue", font=('arial', 12), bg='peachpuff')
    lbl_register.bind('<Enter>', lambda event, label=lbl_register: label.config(font=('arial', 12, 'underline')))
    lbl_register.bind('<Leave>', lambda event, label=lbl_register: label.config(font=('arial', 12)))
    lbl_register.bind('<Button-1>', StaffToggleToRegister)
    lbl_register.grid(row=6, columnspan=3)

    lbl_home = tk.Label(LoginFrame, text="Home Page", fg="Blue", font=('arial', 12), bg='peachpuff')
    lbl_home.bind('<Enter>', lambda event, label=lbl_home: label.config(font=('arial', 12, 'underline')))
    lbl_home.bind('<Leave>', lambda event, label=lbl_home: label.config(font=('arial', 12)))
    lbl_home.bind('<Button-1>', lambda event: create_homepage())
    lbl_home.grid(row=7, columnspan=3)


def RegisterForm():
    global RegisterFrame, lbl_result2
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg='lightslategray')
    RegisterFrame = Frame(root)
    RegisterFrame.pack(side='top', pady=75)
    RegisterFrame.config(bg='lightgoldenrodyellow')

    lbl_login = Label(RegisterFrame, text="Click to Login", fg="Blue", font=('arial', 12, 'underline'),
                      bg='lightgoldenrodyellow')
    lbl_login.grid(row=10, columnspan=2)
    lbl_login.bind('<Enter>', lambda event, label=lbl_login: label.config(font=('arial', 12, 'underline')))
    lbl_login.bind('<Leave>', lambda event, label=lbl_login: label.config(font=('arial', 12)))
    lbl_login.bind('<Button-1>', ToggleToLogin)

    lbl_result2 = Label(RegisterFrame, text="Registration Form:", font=('times new roman', 20, 'bold'), bd=18,
                        bg='lightgoldenrodyellow')
    lbl_result2.grid(row=1, columnspan=2)

    lbl_username = Label(RegisterFrame, text="Username:", font=('times new roman', 16), bd=18,
                         bg='lightgoldenrodyellow')
    lbl_username.grid(row=2)

    lbl_password = Label(RegisterFrame, text="Password:", font=('times new roman', 16), bd=18,
                         bg='lightgoldenrodyellow')
    lbl_password.grid(row=3)

    lbl_confirm_password = Label(RegisterFrame, text="Confirm Password:", font=('times new roman', 16), bd=18,
                                 bg='lightgoldenrodyellow')
    lbl_confirm_password.grid(row=4)

    lbl_firstname = Label(RegisterFrame, text="First Name:", font=('times new roman', 16), bd=18,
                          bg='lightgoldenrodyellow')
    lbl_firstname.grid(row=5)

    lbl_lastname = Label(RegisterFrame, text="Last Name:", font=('times new roman', 16), bd=18,
                         bg='lightgoldenrodyellow')
    lbl_lastname.grid(row=6)

    lbl_dateofbirth = Label(RegisterFrame, text="Date Of Birth:", font=('times new roman', 16), bd=18,
                            bg='lightgoldenrodyellow')
    lbl_dateofbirth.grid(row=7)

    lbl_emailaddress = Label(RegisterFrame, text="Email Address:", font=('times new roman', 16), bd=18,
                             bg='lightgoldenrodyellow')
    lbl_emailaddress.grid(row=8)

    USERNAME_REGISTER.set("Enter Your UserName")
    PASSWORD_REGISTER.set("Enter Your Password")
    CONFIRM_PASSWORD.set("Confirm Your Password")
    FIRST_NAME.set("Enter Your First Name")
    LAST_NAME.set("Enter Your Last Name")
    DATE_OF_BIRTH.set("dd/mm/yyyy")
    EMAIL_ADDRESS.set("Ex: xxxxxxxx@gmail.com")

    username = Entry(RegisterFrame, font=('times new roman', 16), textvariable=USERNAME_REGISTER, width=30)
    username.grid(row=2, column=1, padx=35)
    username.config(fg='grey')
    username.bind('<FocusIn>', lambda event: on_entry_click(event, username, "Enter Your UserName", USERNAME_REGISTER))
    username.bind('<FocusOut>', lambda event: on_focusout(event, username, "Enter Your UserName", USERNAME_REGISTER))

    password = Entry(RegisterFrame, font=('times new roman', 16), textvariable=PASSWORD_REGISTER, width=30)
    password.grid(row=3, column=1, padx=35)
    password.config(fg='grey', show='')
    password.bind('<FocusIn>',
                  lambda event: on_entry_click(event, password, "Enter Your Password", PASSWORD_REGISTER, True))
    password.bind('<FocusOut>',
                  lambda event: on_focusout(event, password, "Enter Your Password", PASSWORD_REGISTER, True))

    confirm_password_entry = Entry(RegisterFrame, font=('times new roman', 16), textvariable=CONFIRM_PASSWORD, width=30)
    confirm_password_entry.grid(row=4, column=1, padx=35)
    confirm_password_entry.config(fg='grey', show='')
    confirm_password_entry.bind('<FocusIn>',
                                lambda event: on_entry_click(event, confirm_password_entry, "Confirm Your Password",
                                                             CONFIRM_PASSWORD, True))
    confirm_password_entry.bind('<FocusOut>',
                                lambda event: on_focusout(event, confirm_password_entry, "Confirm Your Password",
                                                          CONFIRM_PASSWORD, True))

    firstname = Entry(RegisterFrame, font=('times new roman', 16), textvariable=FIRST_NAME, width=30)
    firstname.grid(row=5, column=1, padx=35)
    firstname.config(fg='grey')
    firstname.bind('<FocusIn>', lambda event: on_entry_click(event, firstname, "Enter Your First Name", FIRST_NAME))
    firstname.bind('<FocusOut>', lambda event: on_focusout(event, firstname, "Enter Your First Name", FIRST_NAME))

    lastname = Entry(RegisterFrame, font=('times new roman', 16), textvariable=LAST_NAME, width=30)
    lastname.grid(row=6, column=1, padx=35)
    lastname.config(fg='grey')
    lastname.bind('<FocusIn>', lambda event: on_entry_click(event, lastname, "Enter Your Last Name", LAST_NAME))
    lastname.bind('<FocusOut>', lambda event: on_focusout(event, lastname, "Enter Your Last Name", LAST_NAME))

    dateofbirth = Entry(RegisterFrame, font=('times new roman', 16), textvariable=DATE_OF_BIRTH, width=30)
    dateofbirth.grid(row=7, column=1, padx=35)
    dateofbirth.config(fg='grey')
    dateofbirth.bind('<FocusIn>', lambda event: on_entry_click(event, dateofbirth, "dd/mm/yyyy", DATE_OF_BIRTH))
    dateofbirth.bind('<FocusOut>', lambda event: on_focusout(event, dateofbirth, "dd/mm/yyyy", DATE_OF_BIRTH))

    emailaddress = Entry(RegisterFrame, font=('times new roman', 16), textvariable=EMAIL_ADDRESS, width=30)
    emailaddress.grid(row=8, column=1, padx=35)
    emailaddress.config(fg='grey')
    emailaddress.bind('<FocusIn>',
                      lambda event: on_entry_click(event, emailaddress, "Ex: xxxxxxxx@gmail.com", EMAIL_ADDRESS))
    emailaddress.bind('<FocusOut>',
                      lambda event: on_focusout(event, emailaddress, "Ex: xxxxxxxx@gmail.com", EMAIL_ADDRESS))

    btn_register = Button(RegisterFrame, text="Register", font=('times new roman', 16), width=20, command=Register,
                          bg='blue', fg='white', relief='raised')
    btn_register.grid(row=9, columnspan=2, pady=30)


def StaffRegisterForm():
    global StaffRegisterFrame, lbl_result4
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg='peachpuff')
    StaffRegisterFrame = Frame(root)
    StaffRegisterFrame.place(x=560, y=200)
    StaffRegisterFrame.config(bg='rosybrown')

    lbl_login = Label(StaffRegisterFrame, text="Click to Login", fg="Blue", font=('arial', 12), bg='rosybrown')
    lbl_login.grid(row=8, columnspan=2)
    lbl_login.bind('<Button-1>', StaffToggleToLogin)

    lbl_result4 = Label(StaffRegisterFrame, text="Staff Registration Form:", font=('times new roman', 20, 'bold'),
                        bd=18, bg='rosybrown')
    lbl_result4.grid(row=1, columnspan=2)

    lbl_Staff_name = Label(StaffRegisterFrame, text="Staff Name:", font=('times new roman', 16), bd=18, bg='rosybrown')
    lbl_Staff_name.grid(row=2)

    lbl_password = Label(StaffRegisterFrame, text="Password:", font=('times new roman', 16), bd=18, bg='rosybrown')
    lbl_password.grid(row=3)

    lbl_Position = Label(StaffRegisterFrame, text="Position:", font=('times new roman', 16), bd=18, bg='rosybrown')
    lbl_Position.grid(row=4)

    Staff_name = Entry(StaffRegisterFrame, font=('times new roman', 16), textvariable=STAFF_REGISTER, width=15)
    Staff_name.grid(row=2, column=1, padx=35)

    password = Entry(StaffRegisterFrame, font=('times new roman', 16), textvariable=STAFF_PASSWORD_REGISTER, width=15,
                     show="*")
    password.grid(row=3, column=1, padx=35)

    Position = Entry(StaffRegisterFrame, font=('times new roman', 16), textvariable=POSITION, width=15)
    Position.grid(row=4, column=1, padx=35)

    btn_login = Button(StaffRegisterFrame, text="Register", font=('arial', 15), width=20, command=StaffRegister,
                       bg='blue',
                       fg='white', relief='raised')
    btn_login.bind("<Enter>", lambda e: btn_login.config(bg="lightblue"))
    btn_login.bind("<Leave>", lambda e: btn_login.config(bg="blue"))
    btn_login.grid(row=7, columnspan=2, pady=20)


def ToggleToLogin(event=None):
    RegisterFrame.destroy()
    LoginForm()


def StaffToggleToLogin(event=None):  #switching from register to login page.
    StaffRegisterFrame.destroy()
    StaffLoginForm()


def ToggleToRegister(event=None):
    LoginFrame.destroy()
    RegisterForm()


def StaffToggleToRegister(event=None):  #switching the interface from login to register after user click the register link
    if StaffLoginForm in globals():  #if login form is display, then need to deleted and switch to registration form
        StaffLoginForm.destroy()

    StaffRegisterForm()


def Login():
    Database()
    if USERNAME_LOGIN.get() == "" or PASSWORD_LOGIN.get() == "":
        messagebox.showerror("Error", "Please complete the required fields!")
    else:
        cursor.execute("SELECT * FROM `Customer` WHERE `Username` = ? AND `Password` = ?",
                       (USERNAME_LOGIN.get(), PASSWORD_LOGIN.get()))
        if cursor.fetchone() is not None:
            messagebox.showinfo("Info", "Successfully Login!")
            Pickup_or_Dinein_window()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")
    cursor.close()
    conn.close()


def StaffRegister():
    Database()
    if (STAFF_REGISTER.get() == "" or STAFF_PASSWORD_REGISTER.get() == "" or POSITION.get() == ""):
        messagebox.showerror("Error", "Please complete all the required fields!")
    else:
        try:
            cursor.execute("SELECT * FROM `ADMIN` WHERE `Staff_Name` = ?", (STAFF_REGISTER.get(),))
            if cursor.fetchone() is not None:
                messagebox.showerror("Error", "Staff Name is already taken!")
            else:
                cursor.execute(
                    "INSERT INTO `ADMIN` (Staff_Name, Password, Position) VALUES(?, ?, ?)",
                    (str(STAFF_REGISTER.get()), str(STAFF_PASSWORD_REGISTER.get()), str(POSITION.get())))
                conn.commit()  #save current data to database
                STAFF_REGISTER.set("")
                STAFF_PASSWORD_REGISTER.set("")
                POSITION.set("")
                messagebox.showinfo("Success", "You Successfully Registered. Click to Login")
        except sqlite3.Error as e:
            messagebox.showerror("Error", "Error occurred during registration: {}".format(e))


def StaffLogin():
    Database()
    if STAFF_LOGIN.get() == "" or STAFF_PASSWORD_LOGIN.get() == "":
        messagebox.showerror("Error", "Please complete the required field!")
    else:
        cursor.execute("SELECT * FROM `ADMIN` WHERE `Staff_Name` = ? and `Password` = ?",
                       (STAFF_LOGIN.get(), STAFF_PASSWORD_LOGIN.get()))
        if cursor.fetchone() is not None:
            messagebox.showinfo("Success", "You Successfully Login")
            Home()  # Call Home function after successful login
        else:
            messagebox.showerror("Error", "Invalid Staff Name or password")


def Register():
    Database()
    if USERNAME_REGISTER.get() == "" or PASSWORD_REGISTER.get() == "" or CONFIRM_PASSWORD.get() == "" or FIRST_NAME.get() == "" or LAST_NAME.get() == "" or DATE_OF_BIRTH.get() == "" or EMAIL_ADDRESS.get() == "":
        messagebox.showerror("Error", "Please complete the required fields!")
    elif PASSWORD_REGISTER.get() != CONFIRM_PASSWORD.get():
        messagebox.showerror("Error", "Passwords do not match!")
    else:
        cursor.execute("SELECT * FROM `Customer` WHERE `Username` = ?", (USERNAME_REGISTER.get(),))
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "Username already exists!")
        else:
            cursor.execute(
                "INSERT INTO `Customer` (Username, Password, First_Name, Last_Name, Date_Of_Birth, Email_Address) VALUES(?, ?, ?, ?, ?, ?)",
                (USERNAME_REGISTER.get(), PASSWORD_REGISTER.get(), FIRST_NAME.get(), LAST_NAME.get(),
                 DATE_OF_BIRTH.get(), EMAIL_ADDRESS.get()))
            conn.commit()
            messagebox.showinfo("Info", "Successfully Registered!")
    cursor.close()
    conn.close()


def StaffRegister():
    Database()
    if (STAFF_REGISTER.get() == "" or STAFF_PASSWORD_REGISTER.get() == "" or POSITION.get() == ""):
        messagebox.showerror("Error", "Please complete all the required fields!")
    else:
        try:
            cursor.execute("SELECT * FROM `ADMIN` WHERE `Staff_Name` = ?", (STAFF_REGISTER.get(),))
            if cursor.fetchone() is not None:
                messagebox.showerror("Error", "Staff Name is already taken!")
            else:
                cursor.execute(
                    "INSERT INTO `ADMIN` (Staff_Name, Password, Position) VALUES(?, ?, ?)",
                    (str(STAFF_REGISTER.get()), str(STAFF_PASSWORD_REGISTER.get()), str(POSITION.get())))
                conn.commit()  #save current data to database
                STAFF_REGISTER.set("")
                STAFF_PASSWORD_REGISTER.set("")
                POSITION.set("")
                messagebox.showinfo("Success", "You Successfully Registered. Click to Login")
        except sqlite3.Error as e:
            messagebox.showerror("Error", "Error occurred during registration: {}".format(e))


create_homepage()

if __name__ == '__main__':
    root.mainloop()
