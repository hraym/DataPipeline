from pymongo import MongoClient, ASCENDING, WriteConcern
from pymongo.errors import ConnectionFailure
import logging
from datetime import datetime, timezone

class MongoDBHandler:
    def __init__(self, host='localhost', port=27017, db_name='world_bank_data'):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.logger = logging.getLogger(__name__)

    def test_connection(self):
        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            return True
        except ConnectionFailure:
            self.logger.error("Server not available")
            return False

    def ensure_connection(self):
        if not self.test_connection():
            raise ConnectionError("Failed to connect to MongoDB")

    def validate_data(self, data, indicator_name):
        valid_data = []
        for item in data:
            if all(key in item for key in ['country_code', 'year', 'value']):
                valid_item = {
                    'country_code': item['country_code'],
                    'year': item['year'],
                    'value': item['value']
                }
                if 'country_name' in item:
                    valid_item['country_name'] = item['country_name']
                valid_data.append(valid_item)
            else:
                self.logger.warning(f"Invalid data item: {item}")
        
        self.logger.info(f"Validated {len(valid_data)} out of {len(data)} items for {indicator_name}")
        return valid_data

    def update_indicator_mapping(self, indicator_code, indicator_name):
        mapping_collection = self.db['indicator_mapping']
        mapping_collection.update_one(
            {'code': indicator_code},
            {'$set': {'name': indicator_name}},
            upsert=True
        )

    def get_indicator_name(self, indicator_code):
        mapping_collection = self.db['indicator_mapping']
        mapping = mapping_collection.find_one({'code': indicator_code})
        return mapping['name'] if mapping else None

    def insert_or_update_indicator_data(self, indicator_code, indicator_name, data):
        self.ensure_connection()
        valid_data = self.validate_data(data, indicator_code)
        self.logger.info(f"Inserting/updating {len(valid_data)} valid items for {indicator_code}")
    
        if not valid_data:
            self.logger.warning(f"No valid data to insert for {indicator_code}")
            return
    
        collection = self.db[indicator_code]
        with self.client.start_session() as session:
            with session.start_transaction(write_concern=WriteConcern(w='majority')):
                for item in valid_data:
                    try:
                        item['indicator_name'] = indicator_name  # Add indicator name to each item
                        existing_doc = collection.find_one({
                            'country_code': item['country_code'],
                            'year': item['year']
                        })
                        
                        if existing_doc:
                            self.logger.debug(f"Existing document for {indicator_code}, {item['country_code']}, {item['year']}: {existing_doc}")
                            
                            if existing_doc['value'] != item['value']:
                                collection.update_one(
                                    {'_id': existing_doc['_id']},
                                    {
                                        '$set': {
                                            'value': item['value'],
                                            'indicator_name': indicator_name,
                                            'last_updated': datetime.now(timezone.utc)
                                        }
                                    }
                                )
                                self.logger.info(f"Updated data for indicator {indicator_code}, country {item['country_code']}, year {item['year']}")
                        else:
                            item['last_updated'] = datetime.now(timezone.utc)
                            collection.insert_one(item)
                            self.logger.info(f"Inserted new data for indicator {indicator_code}, country {item['country_code']}, year {item['year']}")
                    except Exception as e:
                        self.logger.error(
                            f"Error processing item for {indicator_code}, {item.get('country_code', 'Unknown')}, {item.get('year', 'Unknown')}: {str(e)}")
                        self.logger.error(f"Item content: {item}")
    
        self.verify_insertion(indicator_code, valid_data)
    
    def get_indicator_data(self, indicator_code, countries=None, start_year=None, end_year=None):
        self.ensure_connection()
        collection = self.db[indicator_code]
        query = {}
        if countries and countries != ["all"]:
            query['country_code'] = {'$in': countries}
        if start_year and end_year:
            query['year'] = {'$gte': start_year, '$lte': end_year}
        
        data = list(collection.find(query))
        self.logger.info(f"Retrieved {len(data)} records for indicator {indicator_code}")
        
        if not data:
            self.logger.warning(f"No data found for indicator {indicator_code} with the given criteria")
        
        return data

    def verify_insertion(self, indicator, data):
        collection = self.db[indicator]
        for item in data:
            stored_item = collection.find_one({'country_code': item['country_code'], 'year': item['year']})
            if not stored_item:
                self.logger.error(f"Failed to store item: {item}")
            else:
                self.logger.debug(f"Successfully stored: {stored_item}")

    def get_missing_data_ranges(self, indicator, countries, start_year, end_year):
        self.ensure_connection()
        collection = self.db[indicator]
        existing_data = collection.find({
            'country_code': {'$in': countries},
            'year': {'$gte': start_year, '$lte': end_year}
        }, {'country_code': 1, 'year': 1, '_id': 0})

        existing_set = set((d['country_code'], d['year']) for d in existing_data)
        all_combinations = set((country, year) for country in countries for year in range(start_year, end_year + 1))
        
        missing_combinations = all_combinations - existing_set
        self.logger.info(f"Found {len(missing_combinations)} missing data points for {indicator}")
        return list(missing_combinations)

    def create_indexes(self):
        self.ensure_connection()
        for collection_name in self.db.list_collection_names():
            collection = self.db[collection_name]
            collection.create_index([('country_code', ASCENDING), ('year', ASCENDING)], unique=True)
        self.logger.info("Created indexes for all collections")

    def get_latest_year(self, indicator):
        self.ensure_connection()
        collection = self.db[indicator]
        result = collection.find_one(sort=[('year', -1)])
        latest_year = result['year'] if result else None
        self.logger.info(f"Latest year for {indicator}: {latest_year}")
        return latest_year

    def close_connection(self):
        if self.client:
            self.client.close()
            self.logger.info("Closed MongoDB connection")