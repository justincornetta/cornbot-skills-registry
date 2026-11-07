import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
const dir=process.argv[2];
if(!dir)throw new Error('Usage: export_pngs.mjs OUTPUT_DIRECTORY');
for(const name of ['jmj-capital-donut','jmj-capital-comparison']){
 const svg=await fs.readFile(path.join(dir,name+'.svg'));
 const width=name.endsWith('donut')?2700:2800;
 await sharp(svg).resize({width}).flatten({background:'#03101e'}).png().toFile(path.join(dir,name+'.png'));
 await sharp(svg).resize({width:1100}).flatten({background:'#03101e'}).png().toFile(path.join(dir,name+'-preview.png'));
}
console.log('Exported both opaque portfolio PNGs.');
