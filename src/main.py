import os
import argparse
import SimpleITK as sitk

def main():
    args = getArgs()
    medianRadius = args.median
    topHatRadius = args.tophat_radius
    minSize = args.minsize

    images = getImages(args.images)

    viewer = sitk.ImageViewer()
    viewer.SetApplication(args.viewer)

    # notes: use aggressive median filter to remove noise
    # structures of interest are the most dense, so remove things of lower density
    for img_orig in images:
        # seems to work ok
        # img = sitk.Median(img, radius=(10, 10))
        # img = sitk.SmoothingRecursiveGaussian(img, sigma=5.)
        # img = sitk.LaplacianSharpening(img)
        # img = sitk.BinaryThreshold(img, lowerThreshold=180, upperThreshold=255, outsideValue=0)
        # img = sitk.ConnectedComponent(img)

        img = sitk.Median(img_orig, radius=(medianRadius, medianRadius)) # param
        #img = sitk.SmoothingRecursiveGaussian(img_orig, sigma=10)
        img = sitk.LaplacianSharpening(img)
        img = sitk.WhiteTopHat(img, kernelRadius=(topHatRadius, topHatRadius)) # param
        img = sitk.OtsuThreshold(img, 0, 1)
        img = sitk.ConnectedComponent(img)

        img_labelMap = sitk.RelabelComponent(img, minimumObjectSize=minSize) # param

        overlay  = sitk.LabelMapOverlay(sitk.Cast(img_labelMap, sitk.sitkLabelUInt32), img_orig, opacity=.85)
        labels = sitk.LabelToRGB(img)

        # print(img_rgb.GetPixelIDTypeAsString())
        # print(img_orig.GetPixelIDTypeAsString())


        viewer.Execute(overlay)
        viewer.Execute(labels)

def getArgs():
    # parse arguments
    parser = argparse.ArgumentParser(
        description="powerhouse segmentation image processing"
    )

    # Users choice of image viewer
    parser.add_argument(
        "--viewer",
        "-v",
        nargs="?",
        help='path to image viewer, default value is "Fiji"',
        default="Fiji",
    )

    # List of image files to process
    parser.add_argument(
        "images", metavar="IMG", nargs="+", help="image filename(s) to process"
    )

    # Median Radius
    parser.add_argument(
        "--median",
        "-m",
        nargs="?",
        help="radius of the structuring element used in the median filter",
        type=int,
        default=7,
    )

    # White Top Hat Radius
    parser.add_argument(
        "--tophat_radius",
        "-t",
        nargs="?",
        help="radius of the structuring element used in the White TopHat algorithm",
        type=int,
        default=10,
    )

    # Minimum size of the final labels
    parser.add_argument(
        "--minsize",
        "-s",
        nargs="?",
        help="remove any labels that are below the specified size",
        type=int,
        default=600,
    )

    return parser.parse_args()



# args: list of strings (filenames)
# returns: array of sitk images
#
def getImages(args):
    images = []
    for fn in args:
        if os.path.isdir(fn) or not os.path.exists(fn):
            print("filename is a directory or does not exist: ", fn)
            args.remove(fn)
        else:
            try:
                images.append(sitk.ReadImage(fn))
            except RuntimeError as e:
                print(e)

    return images

def create_median_close_mask(img, median_iters=3, median_radius=5, binary_thresh=20, close_radius=5, display_mask=False):

    if median_iters > 1:
        median_filter = sitk.MedianImageFilter()
        median_filter.SetRadius(median_radius)
        median = median_filter.Execute(img)

    for i in range(1, median_iters):
        median = median_filter.Execute(median)

    # Convert median into binary
    for i in range(median.GetSize()[0]):
        for j in range(median.GetSize()[1]):
            if median.GetPixel(i, j) > binary_thresh:
                median.SetPixel(i, j, 1)
            else:
                median.SetPixel(i, j, 0)

    close_aperature = sitk.BinaryMorphologicalClosingImageFilter()
    close_aperature.SetKernelRadius(close_radius)
    closed = close_aperature.Execute(median)

    if display_mask:
        view_img = sitk.Image(closed.GetSize()[0], closed.GetSize()[1], sitk.sitkUInt8)

        # Make it visible again
        for i in range(closed.GetSize()[0]):
            for j in range(closed.GetSize()[1]):
                if closed.GetPixel(i, j) == 1:
                    view_img.SetPixel(i, j, 255)

        sitk.ImageViewer().Execute(view_img)

    return closed


def apply_mask(img, mask):
    retval = sitk.Image(img.GetSize()[0], img.GetSize()[1], sitk.sitkUInt8)

    if img.GetSize() != mask.GetSize():
        print("ERROR: IMG SIZE AND MASK SIZE MUST BE EQUAL")
        return

    for i in range(img.GetSize()[0]):
        for j in range(img.GetSize()[1]):
            if mask.GetPixel(i, j) != 0:
                retval.SetPixel(i, j, img.GetPixel(i, j))

    return retval


def highlightByMask(img1, mask):
    print("ehloo")


if __name__ == "__main__":
    main()

