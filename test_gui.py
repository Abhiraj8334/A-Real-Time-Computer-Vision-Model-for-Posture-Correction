import customtkinter as ctk

# Test if GUI can open
try:
    app = ctk.CTk()
    app.title("Test Window")
    app.geometry("400x300")
    
    label = ctk.CTkLabel(app, text="GUI is working!", text_color="green", font=("Arial", 20))
    label.pack(pady=50)
    
    print("GUI window opened successfully!")
    app.after(3000, app.quit)  # Close after 3 seconds
    app.mainloop()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
