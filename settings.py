from fbmq import Page, Template

def init():
    global page
    TABOT_ACCESS_TOKEN = "EAANbYW2bhcwBAHprKcgSrs86S3MFVdVv37auFZBAo4EPzAMTjKNDQuLj9227ai1Agbryvs2QXcHQgf7vHs2Xv0YynvT7XDo4wPAjSHabFyvbJVQfkUkZCJP7PZBRZBcLctaT7MG0aDSJDFZCBbnxcfR8KB48i9YAWLiIAmSmRevoiIfLGWUIY"
    page = Page(TABOT_ACCESS_TOKEN)
    page.show_starting_button("GET_START")
    page.greeting(
        "Hi {{user_first_name}}! TaBot is Messenger Bot to help you know more about Celcom Prepaid Package. Let's Get Started!")
    page.show_persistent_menu([
        Template.ButtonPostBack("Available command ⚛️", 'COMMAND'),
        Template.ButtonWeb("Celcom website 📱", "https://www.celcom.com.my"),
        Template.ButtonPostBack("tabot", 'START')
    ])