"""Globus Harvester.

Usage:
  globus_harvester.py [--onlyharvest | --onlyexport] [--only-new-records] [--export-filepath=<file>] [--export-format=<format>]

Options:
  --onlyharvest             Just harvest new items, do not export anything.
  --onlyexport              Just export existing items, do not harvest anything.
  --only-new-records        Only export records changed since last crawl.
  --export-filepath=<file>  The path to export the data to.
  --export-format=<format>  The export format (gmeta or rifcs).

"""

from docopt import docopt
import sys
import json
import os
import time

from harvester.OAIRepository import OAIRepository
from harvester.CKANRepository import CKANRepository
from harvester.DBInterface import DBInterface
from harvester.HarvestLogger import HarvestLogger
from harvester.TimeFormatter import TimeFormatter
from harvester.Lock import Lock
from harvester.Exporter import Exporter


def get_config_json(repos_json="data/config.json"):
	configdict = {}

	with open(repos_json, 'r') as jsonfile:
		configdict = json.load(jsonfile)

	return configdict


if __name__ == "__main__":

	instance_lock = Lock()
	tstart = time.time()
	arguments = docopt(__doc__)

	global configs
	configs = get_config_json()
	configs['update_log_after_numitems'] = configs.get('update_log_after_numitems', 1000)
	configs['abort_after_numerrors'] = configs.get('abort_after_numerrors', 5)
	configs['record_refresh_days'] = configs.get('record_refresh_days', 30)
	configs['repo_refresh_days'] = configs.get('repo_refresh_days', 1)
	configs['temp_filepath'] = configs.get('temp_filepath', "temp")
	configs['export_filepath'] = configs.get('export_filepath', "data")
	configs['export_batch_size'] = configs.get('export_batch_size', 8000)
	configs['export_format'] = configs.get('export_format', "gmeta")

	main_log = HarvestLogger(configs['logging'])
	main_log.info("Starting... (pid=%s)" % (os.getpid()))

	dbh = DBInterface(configs['db'])
	dbh.setLogger(main_log)

	if arguments["--onlyexport"] == False:
		# Find any new information in the repositories
		for repoconfig in configs['repos']:
			if repoconfig['type'] == "oai":
				repo = OAIRepository(configs)
			elif repoconfig['type'] == "ckan":
				repo = CKANRepository(configs)
			repo.setLogger(main_log)
			repo.setRepoParams(repoconfig)
			repo.setDatabase(dbh)
			repo.crawl()
			repo.update_stale_records(configs['db'])

	if arguments["--onlyharvest"] == True:
		raise SystemExit

	if arguments["--export-format"]:
		configs['export_format'] = arguments["--export-format"]
	if arguments["--export-filepath"]:
		configs['export_filepath'] = arguments["--export-filepath"]

	temp_filepath = configs['temp_filepath']

	exporter = Exporter(dbh, main_log, configs['db'])

	if arguments["--only-new-records"] == True:
		exporter.export_to_file(configs['export_format'], configs['export_filepath'], configs['export_batch_size'], True, configs['temp_filepath'])
	else:
		exporter.export_to_file(configs['export_format'], configs['export_filepath'], configs['export_batch_size'], False, configs['temp_filepath'])

	formatter = TimeFormatter()
	main_log.info("Done after %s" % (formatter.humanize(time.time() - tstart)))

	with open("data/last_run_timestamp", "w") as lastrun:
		lastrun.write(str(time.time()))
	instance_lock.unlock()
