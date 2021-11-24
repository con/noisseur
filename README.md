# noisseur

System for automated verification of entered/displayed information (on another computer)

## The problem

Systems, such as MRI scanner console, do not have means to provision verification of entered data to fulfill desired requirements.
Examples could be the MRI center-wider convention that 
- all `accession number` fields follow some specific format (e.g., match regex `A[0-9]{6}`)
- sequence names follow [ReproIn](http://reproin.repronim.org/) convention (related: https://github.com/ReproNim/reproin/issues/26)

## Desired features/workflow

- video capture device (such as Magewell used in https://github.com/ReproNim/reprostim/) periodically (each second) captures screen
- system is trained on a set of captured images to recognize displays of interest (e.g. exam card entry)
- specific locations are identified to be subject for OCR to be assigned to some metadata field
- validation of the entered metadata is performed and status (overall Ok or list of errors) is displayed to the user/operator on a separate from the captured display

## Possible extensions

- capture more extensive collection of metadata, e.g. not from magewell "sniffer" but from a regular video camera (e.g. for various types of recording which do not consistently export metadata associated with that recording)
