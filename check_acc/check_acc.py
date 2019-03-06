import sys
import os

def check_acc(file_gt, file_pred):

	def parse_line(line):
		line_split = line.split()
		flag = True
		parse_dict = {}
		if 'SELECT' in line_split and \
		   line_split.index('SELECT') != 0:
		   	flag = False
		if 'SELECT' in line_split:
			pos = None
			if 'WHERE' in line_split:
				pos = line_split.index('WHERE')
			else:
				pos = len(line_split)
			select = line_split[line_split.index('SELECT') + 1:pos]
			if len(select) > 0 and select[0] in ['max', 'min', 'count', 'sum', 'avg']:
				parse_dict['agg'] = select[0]
				select = select[1:]
			else:
				parse_dict['agg'] = None
			parse_dict['sel'] = ' '.join(select)
		else:
			parse_dict['sel'] = parse_dict['agg'] = None
		if 'WHERE' in line_split:
			startpos = line_split.index('WHERE') + 1
			cond = []
			and_indices = [i for i, x in enumerate(line_split) if x == "AND"]
			and_indices.append(len(line_split))
			for endpos in and_indices:
				if endpos < startpos:
					continue
				cond_t = line_split[startpos:endpos]
				pos_t = None
				if 'EQL' in cond_t:
					pos_t = cond_t.index('EQL')
				elif 'GT' in cond_t:
					pos_t = cond_t.index('GT')
				elif 'LT' in cond_t:
					pos_t = cond_t.index('LT')
				if pos_t is None:
					flag = False
				else:
					cond.append([' '.join(cond_t[0:pos_t]), cond_t[pos_t], ' '.join(cond_t[pos_t + 1:])])
				startpos = endpos + 1
			parse_dict['cond'] = cond
		else:
			parse_dict['cond'] = None
		return flag, parse_dict


	gt = open(file_gt)
	pred = open(file_pred)
	lines_p = pred.readlines()
	lines_g = gt.readlines()
	if len(lines_p) != len(lines_g):
		print("Different line number!\n")
		return
	tot_err = 0
	for i, (line_p, line_g) in enumerate(zip(lines_p, lines_g)):
		print("=========================")
		print(line_g)
		print(line_p)
		flag_p, dict_p = parse_line(line_p)
		flag_g, dict_g = parse_line(line_g)
		print(flag_p, dict_p)
		print(flag_g, dict_g)
		if flag_p == False or flag_g == False:
			tot_err += 1
			print("{}: Fail!".format(i))
			continue

		if dict_p['sel'] != dict_g['sel'] or dict_p['agg'] != dict_g['agg']:
			tot_err += 1
			print("{}: Fail!".format(i))
			continue

		cond_p = dict_p['cond']
		cond_g = dict_g['cond']
		if cond_p is None and cond_g is None:
			print("{}: Succeed!".format(i))
			continue
		
		if cond_p is None or cond_g is None:
			tot_err += 1
			print("{}: Fail!".format(i))
			continue

		if set(x[0] for x in cond_p) != set(x[0] for x in cond_g):
			tot_err += 1
			print("{}: Fail!".format(i))
			continue

		flag = True
		for idx_p in range(len(cond_p)):
			idx_g = tuple(x[0] for x in cond_g).index(cond_p[idx_p][0])
			if cond_g[idx_g][1] != cond_p[idx_p][1] or cond_g[idx_g][2] != cond_p[idx_p][2]:
				flag = False
				break
		if not flag:
			tot_err += 1
			print("{}: Fail!".format(i))
			continue
		print("{}: Succeed!".format(i))
	print(tot_err)
	return tot_err




check_acc('GROUND_TRUTH', 'RESULT')
