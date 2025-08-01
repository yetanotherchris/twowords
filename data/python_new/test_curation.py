from twowords_utils.word_curation import WordCurator
import os

def test_word_curation():
    # Create test data
    words_dir = r'c:\Users\chris\Documents\GitHub\twowords\data\words'
    output_dir = r'c:\Users\chris\Documents\GitHub\twowords\data\output'

    print('Testing word curation system...')
    print(f'Words dir: {words_dir}')
    print(f'Output dir: {output_dir}')

    # Check if directories exist
    print(f'Words dir exists: {os.path.exists(words_dir)}')
    print(f'Food dishes file exists: {os.path.exists(os.path.join(words_dir, "food_dishes_final.txt"))}')
    print(f'City indices file exists: {os.path.exists(os.path.join(words_dir, "uk_cities_indices.txt"))}')

    # Test loading city coverage indices
    curator = WordCurator(words_dir)
    city_indices = curator.load_city_coverage_indices(words_dir)
    print(f'Loaded {len(city_indices)} city coverage indices')

    if city_indices:
        print('Sample indices:', list(city_indices)[:10])
    
    return city_indices

if __name__ == "__main__":
    test_word_curation()
