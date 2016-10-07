from __future__ import unicode_literals, absolute_import, print_function, division

from operator import itemgetter

from pandas import DataFrame, Series
import numpy
from scipy.cluster.vq import kmeans2
from matplotlib import pyplot

from core.management.commands._community import CommunityCommand
from core.utils.configuration import DecodeConfigAction


def cast_elements_to_floats(lst):
    return [float(flt) for flt in lst]


class Command(CommunityCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="FutureFashionCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})

    def get_community(self):
        community, created = self.model.objects.get_latest_or_create_by_signature("kleding", **self.config)
        return community

    def plot_data(self, canvas, data_frame, color):
        x, y = data_frame.shape
        x_range = range(x)
        y_range = range(y)
        X, Y = numpy.meshgrid(x_range, y_range)
        canvas.plot_surface(X, Y, data_frame.T.as_matrix())

    def handle_community(self, community, **options):
        from mpl_toolkits.mplot3d import Axes3D
        canvas = pyplot.figure().gca(projection='3d')

        clothing_vectors = numpy.array([
            cast_elements_to_floats(individual["vectors"]) for individual in community.kernel.individual_set.all()
        ])
        centroids, labels = kmeans2(clothing_vectors, 10, minit="points")

        clothing_frame = DataFrame()
        clothing_by_cluster = sorted(zip(labels, clothing_vectors), key=itemgetter(0))
        current_label = None
        for label, vector in clothing_by_cluster:
            if label != current_label:
                current_label = label
                clothing_frame = clothing_frame.append(Series(data=centroids[current_label]), ignore_index=True)
            clothing_frame = clothing_frame.append(Series(data=vector), ignore_index=True)

        #centroids_frame = DataFrame(centroids)
        #centroids_frame.T.plot()
        #centroids_frame.drop(range(20, 4096), axis=1, inplace=True)
        #print(centroids_frame.head())


        self.plot_data(canvas, clothing_frame, 'b')
        pyplot.show()
