import re


# keep track of the chain of variables we're trying to resolve
_var_chain = []

def get_value(values, var):

	global _var_chain

	# check to see if the var being asked for
	# is in our chain. If not, then add it, else, bail
	if var in _var_chain :

		message = " get_value : Circular reference detected : " \
				  + "\nvar : " + _var_chain[-1] \
				  + "\nvalue : " + values[_var_chain[-1]] \
				  + "\nchain : " + str(_var_chain)

		_var_chain = []

		raise Exception(message)
	else:
		_var_chain.append(var)

	# get the value of this variable
	if var in values:

		init_val = values[var]

		# check to see if the value has variables in it
		# and try to resolve each variable
		pattern = re.compile("\$\{([a-zA-Z0-9_\-]+)\}")
		for var2 in pattern.findall(values[var]) :

			val2 = get_value(values, var2)
			rep_pat = "\$\{" + var2 + "\}"
			rep = re.subn(rep_pat, val2, values[var])
			values[var] = rep[0]

		_var_chain.remove(var)
		return values[var] 

	else:
		_var_chain = []
		return None

def resolve_values(values):

	keys = values.keys()
	for key in keys : 
		get_value(values,key)


def run_test(test_name, values, final_values, except_flag):

	print "\n*** " + test_name + " ***\n"
	print "Starting Values: " + str(values)

	try :
		resolve_values(values)
	except Exception, e:
		print "Caught exception : " + str(e)
		if except_flag :
			print "\n   PASSED\n"
			return
		else :
			print "\n   FAILED\n"
			return
	
	print "Final Values: " + str(values)
	good_match = True
	for key in values.keys() : 
		if key in final_values : 
			if values[key] != final_values[key] :
				good_match = False
				break
		else:
			good_match = False
			break

	if good_match : 
		print "\n   PASSED\n"
	else :
		print "\n   FAILED\n"


def get_value_test():

	print "\n" + "***** get_value_test *****" + "\n"

	easy = { "A" : "xyz",
		     "B" : "${A}/pqr",
		     "C" : "${A}/${B}",
		     "D" : "${C}/${B}/${A}" }
	easy_final = { "A" : "xyz",
	               "B" : "xyz/pqr",
	               "C" : "xyz/xyz/pqr",
	               "D" : "xyz/xyz/pqr/xyz/pqr/xyz" }
	run_test("Easy Test", easy, easy_final, False)


	bad = { "A" : "${B}",
		    "B" : "${A}" }
	run_test("Indirect Circular", bad, bad, True)

	bad2 = { "A" : "xyz",
	 	     "B" : "${A}/${B}" }
	run_test("Direct Circular", bad2, bad2, True)

	really_bad = { "A" : "${B}",
			       "B" : "${C}",
			       "C" : "${D}",
			       "D" : "${A}" }
	run_test("Deep Circular", really_bad, really_bad, True)

