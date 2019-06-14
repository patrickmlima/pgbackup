from argparse import Action, ArgumentParser

known_drivers = ['local', 's3']

class DriverAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        driver, destination = values
        if driver.lower() not in known_drivers:
            parser.error("Unknown driver. Available drivers are 'local' & 's3'")
        namespace.driver = driver.lower()
        namespace.destination = destination


def create_parser():
	parser = ArgumentParser(description="""
	Back up PostgreSQL databases locally or to AWS S3.
	""")

	parser.add_argument("url", help="URL of the database to backup")
	parser.add_argument("--driver",
		help="how & where to store backup",
		nargs=2,
		metavar=('DRIVER', 'DESTINATION'),
		action=DriverAction,
		required=True)

	return parser

def main():
	import boto3
	import time
	from pgbackup import pgdump, storage

	args = create_parser().parse_args()
	dump = pgdump.dump(args.url)

	if args.driver == 's3':
		timestamp = time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())
		file_name = pgdump.dump_file_name(args.url, timestamp)
		client = boto3.client('s3')
		print(f"Backing database up to {args.destination} in S3 as {file_name}")
		storage.s3(client, dump.stdout, args.destination, file_name)
	else:
		outfile = open(args.destination, 'wb')
		print(f"Backing database up locally to {outfile.name}")
		storage.local(dump.stdout, outfile)

