"""
Mock data for sexual offender registry lookups
This module provides sample data that can be easily replaced with real API calls
"""

import random

# Mock data structure - easily replaceable with real API
MOCK_OFFENDERS = {
    '90210': {
        'count': 2,
        'offenders': [
            {
                'id': 'SO001',
                'name': 'John D.',
                'age': 45,
                'address': '123 Main St',
                'offense_type': 'Sexual assault',
                'conviction_date': '2015-03-15',
                'lat': 34.0901,
                'lng': -118.4065
            },
            {
                'id': 'SO002',
                'name': 'Michael R.',
                'age': 38,
                'address': '456 Oak Ave',
                'offense_type': 'Child endangerment',
                'conviction_date': '2018-07-22',
                'lat': 34.0895,
                'lng': -118.4070
            }
        ]
    },
    '10001': {
        'count': 1,
        'offenders': [
            {
                'id': 'SO003',
                'name': 'Robert K.',
                'age': 52,
                'address': '789 Broadway',
                'offense_type': 'Sexual misconduct',
                'conviction_date': '2016-11-08',
                'lat': 40.7505,
                'lng': -73.9934
            }
        ]
    },
    '77001': {
        'count': 3,
        'offenders': [
            {
                'id': 'SO004',
                'name': 'David L.',
                'age': 41,
                'address': '321 Houston St',
                'offense_type': 'Sexual assault',
                'conviction_date': '2017-02-14',
                'lat': 29.7604,
                'lng': -95.3698
            },
            {
                'id': 'SO005',
                'name': 'James W.',
                'age': 35,
                'address': '654 Texas Ave',
                'offense_type': 'Indecent exposure',
                'conviction_date': '2019-05-30',
                'lat': 29.7589,
                'lng': -95.3677
            },
            {
                'id': 'SO006',
                'name': 'Mark T.',
                'age': 48,
                'address': '987 Main St',
                'offense_type': 'Sexual battery',
                'conviction_date': '2014-09-12',
                'lat': 29.7612,
                'lng': -95.3702
            }
        ]
    }
}

# ZIP codes with no offenders for testing
SAFE_ZIP_CODES = ['12345', '54321', '99999', '11111', '22222']

def get_offender_data_by_zip(zip_code):
    """
    Get offender data for a given ZIP code
    
    Args:
        zip_code (str): 5-digit ZIP code
        
    Returns:
        dict: Dictionary containing count and offender data
        
    Note:
        This function uses mock data. In production, this would be replaced
        with actual API calls to the National Sex Offender Public Website (NSOPW)
    """
    
    # Return mock data if available
    if zip_code in MOCK_OFFENDERS:
        return MOCK_OFFENDERS[zip_code]
    
    # Return safe result for known safe ZIP codes
    if zip_code in SAFE_ZIP_CODES:
        return {
            'count': 0,
            'offenders': []
        }
    
    # For unknown ZIP codes, randomly generate a result
    # This simulates real-world variability
    if random.random() < 0.3:  # 30% chance of having offenders
        num_offenders = random.randint(1, 2)
        return {
            'count': num_offenders,
            'offenders': [
                {
                    'id': f'SO{random.randint(100, 999)}',
                    'name': f'[Name Redacted {i+1}]',
                    'age': random.randint(25, 65),
                    'address': f'[Address Redacted]',
                    'offense_type': random.choice(['Sexual assault', 'Sexual misconduct', 'Child endangerment']),
                    'conviction_date': f'20{random.randint(10, 23)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'lat': 0,  # Would be populated with real coordinates
                    'lng': 0
                } for i in range(num_offenders)
            ]
        }
    else:
        return {
            'count': 0,
            'offenders': []
        }

def replace_with_real_api():
    """
    Placeholder function showing how to replace mock data with real API
    
    In production, this function would:
    1. Make HTTP requests to the NSOPW API
    2. Parse the response data
    3. Return standardized offender data
    
    Example implementation:
    ```python
    import requests
    
    def get_offender_data_by_zip(zip_code):
        api_key = os.environ.get('NSOPW_API_KEY')
        url = f'https://api.nsopw.gov/search?zip={zip_code}&key={api_key}'
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                'count': len(data.get('offenders', [])),
                'offenders': data.get('offenders', [])
            }
        else:
            return {'count': 0, 'offenders': []}
    ```
    """
    pass
