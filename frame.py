import cv2 as cv
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path


class Frame:
    def __init__(self, moscg, frame, frame_number: int, avg: bool = True, hist: bool = False):
        self.frame = frame
        self.number = frame_number
        self.moscg = moscg
        if avg:
            self.avg_color = self.get_color_avg()

    def get_color_avg(self):
        image = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        avg_row_col = np.average(image, axis=0)
        avg_color = np.average(avg_row_col, axis=0)
        avg_color = np.uint8(avg_color)
        return avg_color

    def save_screenshot(self):
        subdir = Path(self.moscg.save_dir)
        subdir.mkdir(exist_ok=True)
        file_path = Path(subdir, "frame%d.jpg" % self.number)
        cv.imwrite(str(file_path), self.frame)


def get_color_cluster(frame: np.ndarray, num_clusters: int):
    image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    # reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))
    # cluster the pixel intensities
    clt = KMeans(n_clusters=num_clusters)
    clt.fit(image)
    return clt


def centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=num_labels)
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
    # return the histogram
    return hist


# the following functions are currently unused and not yet implemented
def plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype="uint8")
    start_x = 0
    # loop over the percentage of each cluster and the color of
    # each cluster
    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        end_x = start_x + (percent * 300)
        cv.rectangle(bar, (int(start_x), 0), (int(end_x), 50), color.astype("uint8").tolist(), -1)
        start_x = end_x

    # return the bar chart
    return bar