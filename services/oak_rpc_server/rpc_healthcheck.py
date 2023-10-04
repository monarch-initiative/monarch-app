#!/usr/bin/env python

from monarch_py.api.config import OakRPCMarshaller

def main():
    try:
        oak = OakRPCMarshaller()

        # run the 'warmup' query from init_semsim()
        # note, this is roughly equivalent to 
        # /v3/api/semsim/compare/MP%3A0010771/HP%3A0004325
        oak.compare( subjects=["MP:0010771"], objects=["HP:0004325"])

    except Exception as ex:
        print(ex)
        exit(1)

if __name__ == '__main__':
    main()
