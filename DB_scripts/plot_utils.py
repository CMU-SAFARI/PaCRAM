def get_mfr(module):
    if module.startswith('H'):
        return 'Mfr. H'
    elif module.startswith('M'):
        return 'Mfr. M'
    elif module.startswith('S'):
        return 'Mfr. S'
    else:
        raise ValueError('Unknown module name: {}'.format(module))
        
def get_pcr_factor(trasns):
    if trasns == 33 or trasns == "33":
        return 1.00
    elif trasns == 27 or trasns == "27":
        return 0.81
    elif trasns == 21 or trasns == "21":
        return 0.64
    elif trasns == 15 or trasns == "15":
        return 0.45
    elif trasns == 12 or trasns == "12":
        return 0.36
    elif trasns == 9 or trasns == "9":
        return 0.27
    elif trasns == 6 or trasns == "6":
        return 0.18
    