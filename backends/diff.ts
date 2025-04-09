import fs from 'fs';

const args = process.argv.slice(2);
if (args.length !== 2) {
  console.error('Usage: bun diff.ts <file1> <file2>');
  process.exit(1);
};

const [file1, file2] = args;
let f1 = JSON.parse(fs.readFileSync(file1, 'utf8'));
let f2 = JSON.parse(fs.readFileSync(file2, 'utf8'));

let changes = 0;
function diff (a: any, b: any) {
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  // for each key
  // if values same, ignore else print
  // if values are objects, recurse
  for (const key of keys) {
    if (a[key] === b[key]) {
      continue;
    }
    if (
      typeof a[key] === 'object'
      && typeof b[key] === 'object'
    ) {
      diff(a[key], b[key]);
    } else {
      changes++;
      console.log(`[${key}: ${a[key]} -> ${b[key]}]`);
    }
  }
};

if (changes === 0) {
  console.log('No changes');
}

diff(f1, f2);