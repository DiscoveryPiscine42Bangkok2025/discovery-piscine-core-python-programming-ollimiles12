import sys
i = 0
if len(sys.argv) > 1:
    sys.exit(1)
while i <= 10:
  print(f"Table de {i}:",i*1,i*2,i*3,i*4,i*5,i*6,i*7,i*8,i*9,i*10)
  i += 1