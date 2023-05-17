class ValidationForms:
    def __init__(self, username, email, password, confirm_password):
        self.username = username
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
    
    
    def ValidateSignUp(self,username,email,password,confirm_password):
        if (password == confirm_password):
            return True
        else:
            return False    
            
        