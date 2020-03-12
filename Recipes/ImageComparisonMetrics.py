import os.path
import numpy as np
from skimage.io import imread, imsave
from skimage.util import img_as_uint, img_as_float32, img_as_ubyte
from skimage.metrics import mean_squared_error, structural_similarity
from skimage.exposure import match_histograms

"""
Calculates SSIM map as a result of the comparison of 2 channels and metrics values (in the log file). 

For the output image, it is highly recommended to use LUT color mapping to better see the variations in the SSIM values
All real SSIM values (ranging from 0 to 1) can be retrieved from the map doing the following: divide intensities by 255 if image is 8-bit, or by 65535 if 16-bit.

Side note: MSE and mean SSIM (and NRMSE, PSNR) values are output in the log
To be able to see the printed info in the log file, set:
File > Options > Logging > Verbosity = everything

Sources: 
https://scikit-image.org/docs/dev/api/skimage.metrics.html?highlight=structural#skimage.metrics.structural_similarity
https://scikit-image.org/docs/dev/auto_examples/color_exposure/plot_histogram_matching.html#sphx-glr-auto-examples-color-exposure-plot-histogram-matching-py


Requirements
------------
numpy (comes with Aivia installer)
scikit-image (comes with Aivia installer)

Parameters
----------
First input: image to compare (e.g.Deep Learning restored image)
Second input: reference (e.g. Ground Truth image), the one adjusted by histogram matching.

Returns
----------
First output: calculated SSIM map
Second output: reference image transformed with histogram matching

"""

# [INPUT Name:inputRTImagePath Type:string DisplayName:'Input Restored Image']
# [INPUT Name:inputGTImagePath Type:string DisplayName:'Input Ground Truth Image']
# [OUTPUT Name:resultPath Type:string DisplayName:'SSIM image']
# [OUTPUT Name:resultPathAdj Type:string DisplayName:'GT Hist match image']
def run(params):
	RTimageLocation = params['inputRTImagePath']
	GTimageLocation = params['inputGTImagePath']
	resultLocation = params['resultPath']
	resultLocationAdj = params['resultPathAdj']
	
	# Checking existence of temporary files (individual channels)
	if not os.path.exists(RTimageLocation):
		print(f'Error: {RTimageLocation} does not exist')
		return; 
	if not os.path.exists(GTimageLocation):
		print(f'Error: {GTimageLocation} does not exist')
		return; 
		
	# Loading input images
	RTData = imread(RTimageLocation)
	GTData = imread(GTimageLocation)
	print(f'Dimensions of Restored image: {RTData.shape}')
	print(f'Dimensions of GT image: {GTData.shape}')
	
	# Histogram matching
	matched_GTData = match_histograms(GTData, RTData).astype(RTData.dtype)
	
	# MSE measurement
	# valMSE = skimage.measure.compare_mse(RTData, GTData) # deprecated in scikit-image 0.18 
	valMSE = mean_squared_error(RTData, matched_GTData)
	print(f'___ MSE = {valMSE} ___')	# Value appears in the log if Verbosity option is set to 'Everything'
	
	# SSIM measurement
	outFullSSIM = structural_similarity(RTData, matched_GTData, full=True)
	
	# Extracting mean value (first item)
	outMeanSSIM = outFullSSIM[0]
	print(f'___ Mean SSIM = {outMeanSSIM} ___')
	
	# Extracting map (second item)
	outSSIM = outFullSSIM[1]
	print(f'Bit depth of SSIM array: {outSSIM.dtype}')
	
	# Convert output array whose range is [0-1] to adjusted bit range (8- or 16-bit)
	if RTData.dtype is np.dtype('u2'):
		outputData = img_as_uint(outSSIM)
	elif RTData.dtype is np.dtype('f4'):
		outputData = img_as_float32(outSSIM)	# necessary?
	else:
		outputData = img_as_ubyte(outSSIM)
	
	imsave(resultLocation, outputData)	
	imsave(resultLocationAdj, matched_GTData)
