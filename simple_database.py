def read_input(line):
	num_spaces_seen = 0
	op, k, v = [], [], []
	i = 0
	while i < len(line) and num_spaces_seen != 2:
		if line[i] == " ":
			num_spaces_seen += 1
		else:
			if num_spaces_seen == 0:
				op.append(line[i])
			elif num_spaces_seen == 1:
				k.append(line[i])
		i += 1
	
	while i < len(line):
		v.append(line[i])
		i += 1
	return "".join(op), "".join(k), "".join(v)

def read_first_comma(line):
	num_commas_seen = 0
	k, v = [], []
	i = 0
	while num_commas_seen < 1:
		if line[i] == ",":
			num_commas_seen += 1
		else:
			k.append(line[i])
		i += 1
	while i < len(line):
		if line[i] == "\n":
			break
		v.append(line[i])
		i += 1
	return "".join(k), "".join(v)

def db_get(k, hash_index):
	segment_num = -1
	filename = ""
	if int(k) in hash_index:
		segment_num = get_segment_num()
		filename = "database_segment" + str(segment_num) + ".csv"
	else:
		segment_num = get_segment_num()
		for i in range(segment_num - 1, -1, -1):
			d = load_index(i)
			if int(k) in d:
				segment_num = i
				filename = "database_segment" + str(segment_num) + ".csv"
				hash_index = d
				break
	if segment_num == -1:
		return None

	ans = None
	with open(filename, "r") as f:
		offset = hash_index[int(k)]
		f.seek(offset)
		line = f.readline()[:-1]

		k_i, v_i = read_first_comma(line)
		if int(k) == int(k_i):
			ans = v_i
	return ans

def write_globals(d):
	filename = "globals.csv"
	with open(filename, "w") as f:
		for k, v in d.items():
			f.write(k + "," + str(v) + "\n")

def get_segment_num():
	filename = "globals.csv"
	if not os.path.exists("globals.csv"):
		d = {"segment_num": 0}
		write_globals(d)

	k = "segment_num"
	with open(filename, "r") as f:
		while f:
			line = f.readline()
			if line == "":
				break
			line = line[:-1]

			k_i, v_i = line.split(",")
			if k == k_i:
				return int(v_i)
	raise Exception("segment_num not in globals.csv")

import shutil
def compact_segments():
	segment_num = get_segment_num()
	for i in range(segment_num - 1, -1, -1):
		filename = "database_segment" + str(i) + ".csv"
		hash_index = load_index(i)
		new_filename = "database_segment" + str(i) + ".csv.tmp"
		new_hash_index = {}
		with open(filename, 'r') as fr:
			with open(new_filename, 'w') as fw:
				for k, offset in hash_index.items():
					fr.seek(offset)
					line = fr.readline()[:-1]
					new_offset = fw.tell()
					fw.write(line + "\n")
					new_hash_index[k] = new_offset
		shutil.move(new_filename, filename)
		save_index(new_hash_index, i)

SEGMENT_SIZE = 64000 # 64 kb segments
def db_set(k, v, hash_index):
	segment_num = get_segment_num()
	filename = "database_segment" + str(segment_num) + ".csv"
	do_write_new_file = False
	with open(filename, 'a') as f:
		offset = f.tell()
		if offset >= SEGMENT_SIZE:
			save_index(hash_index, segment_num)
			do_write_new_file = True
		else:
			f.write(k + "," + v + "\n")
			hash_index[int(k)] = offset

	if do_write_new_file:
		write_globals({"segment_num": segment_num + 1})
		segment_num = get_segment_num()
		filename = "database_segment" + str(segment_num) + ".csv"
		hash_index = {}
		with open(filename, 'a') as f:
			offset = f.tell()
			f.write(k + "," + v + "\n")
			hash_index[int(k)] = offset

		compact_segments()
	return hash_index

import os
def load_index(segment_num):
	filename = "database_segment" + str(segment_num) + "_index.csv"
	if not os.path.exists(filename):
		return {}

	d = {}
	with open(filename, "r") as f:
		while f:
			line = f.readline()
			if line == "":
				break
			line = line[:-1]

			k, offset = line.split(",")
			d[int(k)] = int(offset)
	return d

def save_index(d, segment_num):
	filename = "database_segment" + str(segment_num) + "_index.csv"
	with open(filename, "w") as f:
		for k, offset in d.items():
			f.write(str(k) + "," + str(offset) + "\n")

op_decoder = {
	"db_get": db_get,
	"db_set": db_set
}
hash_index = load_index(get_segment_num())
while True:
	line = input()
	if line == "exit":
		segment_num = get_segment_num()
		save_index(hash_index, segment_num)
		break
	op, k, v = read_input(line)
	if not k and not v:
		print("Invalid input")
		continue

	op = op_decoder[op]
	if op == db_get:
		v = op(k, hash_index)
		if not v:
			print("Not found")
		else:
			print(v)
	elif op == db_set:
		if not v:
			print("No value")
			continue
		hash_index = op(k, v, hash_index)
		print("Done!")
	else:
		print("Invalid input")
		continue