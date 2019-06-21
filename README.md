# cli-gophish-guide
A script to help automate campaign creation in GoPhish

    Format: ./phish.py <title> <sendername> <senderemail> <targetlist.csv> <email.html> <emailsubject> <pageurl> <page.html> <launchtime>

    eg: ./phish.py "Campaign Name" "John Doe" jdoe@mail.com targets.csv email.html "Email Subject Line" http://insecure.com page.html 2018/06/29@14:30
        ./phish.py "Phish Test Title" "JK Rowling" jkr@mail.com /path/targets.csv email.html "New Book" https://login.phishing.com page.html 1999/12/31@23:59

         title.............name for new campaign objects
         sendername........first and last name as should appear in email header
         senderemail.......address as should appear in email header
         targetlist........csv file (fieldnames=First Name,Last Name,Email,Position)
         email.html........contents of email in html format
         emailsubject......subject line as will appear in email
         pageurl...........phony link address to be used in email
         page.html.........contents of landing page in html format
         launchtime........date and time (24hr) to send email

    Alternative:
             -g................campaign creation walk through

    !format for launchtime MUST use format YYYY/MM/DD@HH:MM [eg: 2018/06/14@4:22]
