# concatinate two strings
# into a result
def concat(a,b):
  result = ''

  for char in a:
    result += char

  for char in b:
    result += char

  return result

x = 'he'
y = 'llo'

# or just r = x + y
r = concat(x,y)

print(r)
