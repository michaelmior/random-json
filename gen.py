import collections
import getopt
import json
import random
import string
import sys


ARRAY_FRACTION = 0.5


flat_paths = collections.defaultdict(lambda: set())
array_paths = {}


def random_string(length=5):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def random_value():
    """Generate a random value to insert in the object"""
    return random.randint(0, 10000)


def random_path(length):
    """Produce a random path of the given length"""
    return '.'.join(random_string() for _ in range(length))


def set_value(doc, path, value):
    """Set a value at the dot-separated path string in the document"""
    parts = path.split('.')
    for part in parts[:-1]:
        if part not in doc:
            doc[part] = {}
        doc = doc[part]

    doc[parts[-1]] = value


def generate_json(num_attributes, total_nesting):
    """Generate an object with the given number of attributes and nesting"""
    global array_paths, flat_paths

    # Partition attributes based on nesting
    nesting_indexes = set(range(total_nesting))
    nested_picks = set()
    for _ in range(num_attributes):
        n = random.choice(tuple(nesting_indexes))
        nesting_indexes.remove(n)
        nested_picks.add(n)

    # Group attributes by the nested depth
    nested_picks = list(sorted(nested_picks))
    attr_counts = collections.defaultdict(lambda: 0)
    for i in range(1, len(nested_picks)):
        attr_counts[nested_picks[i] - nested_picks[i - 1]] += 1
    nesting = sum(k * v for (k, v) in attr_counts.items())
    attr_counts[total_nesting - nesting] += 1
    attr_counts = dict(attr_counts)

    # Decide if each attribute should be flat or an array
    array_counts = {}
    flat_counts = {}
    for (k, v) in attr_counts.items():
        if random.random() > ARRAY_FRACTION:
            array_counts[k] = v
        else:
            flat_counts[k] = v

    # Generate new array paths if needed
    for (depth, _) in array_counts.items():
        if depth not in array_paths:
            new_path = random_path(depth)
            while new_path in array_paths.values():
                new_path = random_path(depth)
            array_paths[depth] = new_path

    # Generate new flat paths if needed
    for (depth, count) in flat_counts.items():
        while len(flat_paths[depth]) < count:
            new_path = random_path(depth)
            while new_path in flat_paths[depth]:
                new_path = random_path(depth)
            flat_paths[depth].add(new_path)

    doc = {}

    # Assign array values
    for (depth, count) in array_counts.items():
        set_value(doc,
                  array_paths[depth],
                  [random_value() for _ in range(depth)])

    # Assign flat values
    for (depth, count) in flat_counts.items():
        for path in random.sample(flat_paths[depth], count):
            set_value(doc, path, random_value())

    return doc


def usage(out=sys.stdout):
    """Print usage information"""
    out.write(' '.join([
        'usage: %s' % sys.argv[0],
        '[-c|--count <count>]',
        '[-a|--atributes <attributes>]',
        '[-n|--nesting <nesting>]\n'
    ]))


def main():
    try:
        opts, _ = getopt.getopt(sys.argv[1:],
                                'hc:a:n:',
                                ['help', 'count=', 'attributes=', 'nesting='])
    except getopt.GetoptError as err:
        sys.stderr.write(str(err) + '\n')
        usage(sys.stderr)
        sys.exit(2)

    count = 10
    attributes = 10
    nesting = 20
    for opt, value in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--count"):
            count = int(value)
        elif opt in ("-a", "--attributes"):
            attributes = int(value)
        elif opt in ("-n", "--nesting"):
            nesting = int(value)
        else:
            assert False, "unhandled option"

    for _ in range(count):
        print(json.dumps(generate_json(attributes, nesting)))


if __name__ == '__main__':
    main()
