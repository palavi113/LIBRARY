from tasks import add

result = add.delay(4,6)
# result.ready()
result.wait(timeout=5)
print(result.get())
