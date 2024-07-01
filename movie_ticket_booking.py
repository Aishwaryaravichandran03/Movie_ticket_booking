import sqlite3
import smtplib
from datetime import datetime

#connect to sqlite3 database
conn = sqlite3.connect('cinema.db')
c = conn.cursor()

#create tables
def create_tables():
    #movies table
    c.execute("create table if not exists movies (title varchar(70) unique, available_seats int, ticket_price int)")
    #bookings table
    c.execute("create table if not exists bookings (movie_name varchar(70), num_tickets int, total_price int)")    
    # Movie titles ,available seats and their ticket prices
    titles = ["aranmanai 4", "manjummal boys", "garudan", "pt sir", "maharaja", "star"]
    ticket_prices = [450, 500, 489, 300, 545, 300]
    available_seats = 100     
    for title, price in zip(titles, ticket_prices):
        c.execute("insert or ignore into movies (title, available_seats, ticket_price) values (?, ?, ?)", (title, available_seats, price))   
    conn.commit()

# show movies
def show_movies():
    c.execute("select title, available_seats, ticket_price from movies")
    movies = c.fetchall()
    for movie in movies:
        title, available_seats, ticket_price = movie  
        print(f"{title} -> Available Seats: {available_seats}, Ticket Price: Rs.{ticket_price}")

#book ticket
def book_ticket(movie_name, num_tickets):
    c.execute("select available_seats, ticket_price from movies where title = ?", (movie_name,))
    movie_info = c.fetchone()
    
    if movie_info is None:
        print(f"Movie '{movie_name}' not found.")
        return False, 0
    available_seats, ticket_price = movie_info
    
    if available_seats >= num_tickets:
        new_seats = available_seats - num_tickets
        c.execute("update movies set available_seats = ? where title = ?", (new_seats, movie_name))
        conn.commit()
        total_price = num_tickets * ticket_price
        c.execute("insert into bookings (movie_name, num_tickets, total_price) values (?, ?, ?)", (movie_name, num_tickets, total_price))
        conn.commit()
        return True, total_price
    else:
        print(f"Failed to book {num_tickets} tickets for '{movie_name}'. Not enough seats available.")
        return False, 0
        
# send email
def send_email(movie_name, num_tickets, total_price, customer_email):
    sender_email = "your_email_id.com" 
    sender_password ="email_password"
    receiver_email = customer_email
    subject = "Your Movie Ticket Details"
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Email content
    email_content = f"Subject: {subject}\nDear Customer,\nThank you for booking your movie ticket with us. Here are your ticket details:\n\nMovie Name : {movie_name}\nSeat : Row A, Seats {num_tickets}\nPrice : Rs.{total_price}\nBooking Date and Time : {current_datetime}\n\n Enjoy the show! "   
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.starttls()
        s.login(sender_email, sender_password)
        s.sendmail(sender_email, receiver_email, email_content)
        s.quit()
        print("Email sent successfully!")
    except:
        print("Failed to send email")
        
#main
def main():
    create_tables()
    while True:
        print("\nAvailable Movies:")
        show_movies()
        choice = input("Enter the movie name to book tickets or 'q' to quit: ")
        if choice.lower() =="q":
            break
        else:
            movie_name = choice
            num_tickets = int(input("Enter the number of tickets to book: "))
            customer_email = input("Enter the customer's email: ")
            success, total_price = book_ticket(movie_name, num_tickets)
            if success:
                print(f"Total price: Rs.{total_price}")
                send_email(movie_name, num_tickets, total_price, customer_email)

main()