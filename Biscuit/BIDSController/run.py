from Biscuit.BIDSController.BIDSFolder import BIDSFolder


root1 = "C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt\\BIDS\\test1"  # noqa
root2 = "C:\\Users\\MQ20184158\\Documents\\MEG data\\rs_test_data_for_matt\\BIDS\\test2"  # noqa

a = BIDSFolder(root1)
b = BIDSFolder(root2)
pa = a.project('WS001')
pb = b.project('WS001')
new_sub = pb.subject(4)
print(pa)
print(pb)

pa.add(new_sub)
