// Fit the complete 16:9 report sheet to CSS-pixel viewport dimensions.
// Browser chrome is already excluded from innerWidth/innerHeight.
export const SHEET={width:1600,height:900,padding:12};
export function fitViewport(width,height,expanded=false){
 if(expanded||!Number.isFinite(width)||!Number.isFinite(height)||width<1000||height<500)return null;
 const scale=Math.min((width-2*SHEET.padding)/SHEET.width,(height-2*SHEET.padding)/SHEET.height);
 return {scale,width:SHEET.width*scale,height:SHEET.height*scale};
}
