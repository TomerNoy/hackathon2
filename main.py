import mail_api
import subprocess
from tkinter import *
from tkinter import messagebox
from threading import Timer
from PIL import Image, ImageTk


root = Tk()
root.title("Temp Mail")

custom_name_input = StringVar()  # input by usr

is_random = BooleanVar()  # checkbox input

displayed_mails = []  # displayed emails in listbox


def fetch_emails(mail):
    # request api for new emails
    mails = mail_api.get_api_inbox(mail)

    for msg in mails:
        id = msg['id']

        # if displayed_mails empty -> append
        if not displayed_mails:
            apply_msg(msg)
        else:
            # if this mail not in displayed_mails-> append
            if not any(e['id'] == id for e in displayed_mails):
                apply_msg(msg)


def apply_msg(msg):
    # gets am email and adds to listbox & displayed_mails
    displayed_mails.append(msg)
    listbox.insert(
        END, f"from: {msg['from']}   subject: {msg['subject']}    date: {msg['date']}   id: {msg['id']}"
    )


class RepeatTimer(Timer):
    # a solution for cancellable time interval with params
    mail = ''

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(RepeatTimer.mail)


timer = RepeatTimer(4, fetch_emails)  # call fetch_emails every 4 sec


def popup(): return messagebox.showwarning(
    'warning', 'name can\'t be empty unless random')


def switch(isRan):
    # random name checkbox
    custom_name_entry['state'] = 'disabled' if isRan else 'normal'


def start_cmd(isRan, name):
    # in case name is empty and not randomly generated we show a warning
    if name == '' and not isRan:
        return popup()

    # we call api to create the new mail
    mail = mail_api.start_mail(isRan, name)

    # notify on errors
    if mail == '':
        notify.config(text='oops... something went wrong')
        return

    # notify on success
    notify.config(
        text=f'your temp email is {mail}, copied to clipboard')
    emails_label.config(text='standing by for new emails...')

    # starting the fetch emails 5sec interval
    RepeatTimer.mail = mail
    timer.start()


def quit():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        timer.cancel()  # on quit we first need to cancel the 5sec interval
        root.destroy()


def open_file_cb(event):
    # opens the corresponding email file previously saved on disk using built in event
    w = event.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    split_list = value.split()
    id = split_list[-1]
    file_path = f'Inbox/{id}.txt'
    subprocess.call(['open', file_path])


# title
title = Label(text=f"Temporary Email Generator", font=(
    "Raleway", 30, 'bold'))
title.grid(row=0, column=1, columnspan=2, pady=30)

# image icon
img = Image.open('icon.ico')
resize_img = img.resize((80, 80))
image = ImageTk.PhotoImage(resize_img)
img_label = Label(image=image)
img_label.grid(row=0, column=0, padx=30, sticky=W)

# custom email name
custom_name = Label(text=f"Custom Email Name:", font=(
    "Raleway", 16))
custom_name.grid(row=1, column=0, padx=30, sticky=W)
# custom email name entry
custom_name_entry = Entry(textvariable=custom_name_input, state='normal')
custom_name_entry.grid(row=1, column=1, sticky=W)

# check box
check_box = Checkbutton(text='use random', variable=is_random,
                        command=lambda: switch(is_random.get()), onvalue=1, offvalue=0)
check_box.grid(row=1, column=2, pady=10)

# start button
start_btn = Button(
    text='Start',
    font=("Raleway", 16, 'bold'),
    width=10,
    command=lambda: start_cmd(is_random.get(), custom_name_input.get()),
    pady=5,

)
start_btn.grid(row=1, column=3, padx=30)

# notifications
notify = Label(text='')
notify.grid(row=3, column=0, columnspan=4, padx=30, sticky=W)

# emails list title
emails_label = Label(text='Emails')
emails_label.grid(row=4, column=0, pady=10, padx=30, sticky=W)

# list of emails fetched
listbox = Listbox(height=6, selectmode='extended')
listbox.bind('<Double-Button-1>', open_file_cb)
listbox.bind('<Return>', open_file_cb)
listbox.grid(column=0, row=5, columnspan=4, sticky='nwes', padx=30)

# quit button
quit_button = Button(text='Quit', width=10,
                     command=lambda: quit(), pady=5, font=("Raleway", 16, 'bold'), fg='#14213d')
quit_button.grid(row=11, column=1, columnspan=4, padx=30, pady=20, sticky=E)
root.protocol("WM_DELETE_WINDOW", quit)

root.mainloop()
