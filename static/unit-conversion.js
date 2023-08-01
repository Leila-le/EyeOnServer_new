function conversionSize(sizeInBytes){
    if( sizeInBytes==='error')
        sizeInBytes=0;
    sizeInBytes=parseInt(sizeInBytes);
    const sizeInGB = sizeInBytes / (1024 * 1024 * 1024);
    return sizeInGB.toFixed(2) + 'GB';
}
