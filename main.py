from dotenv import dotenv_values

conf = dotenv_values(".env")

print(conf['COOKIE_NAME'], conf['COOKIE_VALUE'])
strData = [conf['FBC_LT6']][0]
fbc = strData.split(",")
print(fbc)
print(conf['FBC_LF'].split(","))

# search and replace the COOKIE_NAME & COOKIE_VALUE values
# in the .env file
search_text = conf['COOKIE_NAME']
replace_text = '__ac_'

# open the file in a read mode
f = open(".env", "r")
# Reading the content of the file using the read() function them in a new variable
data = f.read()
# Searching and replacing the text using the replace() function
data = data.replace(search_text, replace_text)
# open file in the write mode
fw = open(".env", "w")
# Writing the replaced data in our text (.env) file
fw.write(data)

f.close()
fw.close()
