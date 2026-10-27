we are not making the OCR from 0 we will use existing OCR and text or pdf extrator solutions 

for this we are using : https://github.com/PaddlePaddle/PaddleOCR

simce its OCR an NVIDIA GPU IS REQUIRED AND IS A MIMIMUM REQUIREMENT OR RECOMENDED IF U WANT BETTER RESULTS BUTS FOR NOW A CUDA ENABLED DEVICE IS A MUST 
uv add pymupdf "paddleocr[doc-parser]"
another we are using is uv add pymupdf
why  pymupdf?
it prepares the PDF and detects which pages need OCR

make chnages in the config.py for variavble and file and folder paths 


