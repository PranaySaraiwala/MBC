import json
x=json.dumps({"name": "John", "age": 30})
x=json.dumps(["apple", "bananas"])
x=json.dumps(("apple", "bananas"))
x=json.dumps("hello")
x=json.dumps(42)
x=json.dumps(31.76)
x=json.dumps(True)
x=json.dumps(False)
x=json.dumps(None)

print(x)


