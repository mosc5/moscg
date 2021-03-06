import cv2 as cv
from pathlib import Path
import numpy as np
import frame
import argparse
from sklearn.cluster import KMeans


class Moscg:
    def __init__(self, movie_path, num_clusters: int = 4, skip_frames: int = 99, save_adjacent: int = 0):
        self.movie_path = movie_path
        self.num_cluster = num_clusters
        self.skip_frames = skip_frames
        self.save_adj = save_adjacent
        self.save_dir = Path("res", movie_path.stem)
        self.movie = None
        self.open_movie()

    def open_movie(self):
        if self.movie is None or not self.movie.isOpened():
            assert self.movie_path.is_file(), "Movie file does not exist"
            print('Opening movie %s' % str(self.movie_path))
            self.movie = cv.VideoCapture(str(self.movie_path), cv.CAP_ANY)
        return self.movie

    def get_list_cluster(self, lst):
        clt = KMeans(self.num_cluster)
        clt.fit(lst)
        return clt

    def run(self):
        """
           Analyze average color of each frame. Build clusters and output one screenshot each.
           :return:
        """
        self.open_movie()
        frame_lst = []
        color_lst = []
        print('Analyzing frames...')
        current_frame = 0
        while self.movie.isOpened():
            ret, movie_frame = self.movie.read()
            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            frames = frame.Frame(self, movie_frame, current_frame)
            frame_lst.append(frames)
            color_lst.append(frames.avg_color)
            current_frame += self.skip_frames + 1
            print("Current frame: %i" % current_frame)
            self.movie.set(cv.CAP_PROP_POS_FRAMES, current_frame-1)

        list_cluster = self.get_list_cluster(color_lst)
        print('Finding best matches...')
        for arr in list_cluster.cluster_centers_:
            lowest_dist = 1000
            frame_number = 0
            for i, color in enumerate(color_lst):
                dist = np.linalg.norm(color - arr)
                if dist < lowest_dist:
                    lowest_dist = dist
                    frame_number = i
            frame_lst[frame_number].save_screenshot()
            if self.save_adj:
                frame_lst[frame_number].save_adjacent_frames(self.save_adj)

        print('Screenshots saved. Run finished.')
        self.movie.release()
        cv.destroyAllWindows()


# TODO: implement hist run function in OOP
def run_hist(movie_path: Path, n_clusters: int):
    """
    :param movie_path:
    :param n_clusters:
    :return:
    """
    assert movie_path.is_file(), "File does not exist"
    print('Opening movie %s' % str(movie_path))
    movie = cv.VideoCapture(str(movie_path), cv.CAP_ANY)
    cluster_lst = []
    print('Analyzing frames...')
    while movie.isOpened():
        ret, frame = movie.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # cluster = frames.get_color_cluster(frame, n_clusters)
        # cluster_lst.append(cluster)
        # hist = frames.centroid_histogram(cluster)
        # bar = frames.plot_colors(hist, cluster.cluster_centers_)
        # # show our color bar
        # plt.figure()
        # plt.axis("off")
        # plt.imshow(bar)
        # plt.show()

    movie.release()
    cv.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Movie screen grabber")
    parser.add_argument('scenario', type=str,
                        help='Set the Path of the video file.')
    parser.add_argument('--num', '-n', nargs='?', type=int, default=4,
                        help='Number of screenshots.')
    parser.add_argument('--skip', '-s', nargs='?', type=int, default=99,
                        help='Number of skipped frames.')
    parser.add_argument('--save_adjacent', nargs='?', type=int, default=0,
                        help='Number of extra saved frames in each direction.')
    p_args = parser.parse_args()

    foo = Moscg(Path(p_args.scenario), p_args.num, p_args.skip, p_args.save_adjacent)
    foo.run()


if __name__ == '__main__':
    main()
