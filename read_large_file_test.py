# one row is 64 bytes
# Multiply to 640 kb
line = """db_set 42 {"name": "London", "attractions": ["Big Ben", "London Eye"]}"""
num_rows = 1000 * 2

filename = "read_large_file_test.txt"
with open(filename, "w") as f:
	for i in range(num_rows):
		f.write(line + "\n")
