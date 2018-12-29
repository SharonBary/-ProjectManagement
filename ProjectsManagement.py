#Sharon Bary ID - 305014946 ©

import unittest


class Activity:
    def __init__(self, id_, name, duration, predecessor_ids):

        self.id = id_
        self.name = name
        self.duration = duration
        self.predecessor_ids = predecessor_ids
        self.early_start = None
        self.early_finish = None
        self.late_start = None
        self.late_finish = None
        self.slack = None
        self.predecessors = {}  # {Activity_id : Activity}
        self.is_critical = False
        self.im_looking_at = []

    def __str__(self):
        res = "Name: %s\nid: %s\nDuration: %s\nPredecessor_ids: " % (self.name, self.id, self.duration)
        if not self.predecessor_ids:
            res += "None \n"
        else:
            res += "%s \n" % self.predecessor_ids
        res += "early_start: %s\nearly_finish: %s\n" \
               "late_start: %s\n" \
               "late_finish: %s\n" \
               "slack: %s\n" \
               "is_critical: %s\n" % (
                   self.early_start, self.early_finish, self.late_start, self.late_finish, self.slack, self.is_critical)

        return res

    def set_predecessors(self, all_activities):

        for predecessor in self.predecessor_ids:
            self.predecessors[predecessor] = all_activities[predecessor]

    def calculate_early_start(self):
        if len(self.predecessors) == 0:
            self.early_start = 0
        else:
            highest_early_finish = 0
            for predecessor_id in self.predecessors:
                if predecessor_id != self.id:
                    predecessor = self.predecessors[predecessor_id]
                    if predecessor.early_finish > highest_early_finish:
                        highest_early_finish = predecessor.early_finish
            self.early_start = highest_early_finish

    def calculate_early_finish(self):
        self.early_finish = self.early_start + self.duration

    """check what is the late_finish for the specific Activity (self)"""

    def calculate_late_finish(self):
        for predecessor_id in self.predecessors:
            predecessor = self.predecessors[predecessor_id]
            if predecessor.late_finish is None:
                predecessor.late_finish = self.late_start
            if predecessor.late_finish >= self.late_start:
                predecessor.late_finish = self.late_start

    def calculate_late_start(self):
        self.late_start = self.late_finish - self.duration

    def calculate_slack(self):
        self.slack = self.late_start - self.early_start

    def calculate_is_critical(self):
        if self.slack == 0:
            self.is_critical = True
        else:
            self.is_critical = False


class Project:
    def __init__(self, _activities=None):

        if _activities is None:
            self.activities = {}
        else:
            self.activities = _activities  # dictionary in the form {activity_id, Activity}
            self.set_activity_predicessors()
            self.forward_pass()
            self.backward_pass()
        self.biggest_early_finish = 0

    def __str__(self):
        res = "The activities are:\n\n"
        for activity in self.activities:
            res += self.activities[activity].__str__() + "\n"
        return res

    def set_activity_predicessors(self):
        for activity in self.order_activities(self.activities, False):
            activity.set_predecessors(activity.predecessors)
        # activity.set_predecessors(self.activities)

    def forward_pass(self):  # 1
        for activity in self.order_activities(self.activities, False):
            activity.calculate_early_start()
            activity.calculate_early_finish()
            if activity.early_finish > self.biggest_early_finish:
                self.biggest_early_finish = activity.early_finish

    def looking_at(self):

        for activity_id_looking in self.activities:
            self.activities[activity_id_looking].im_looking_at = []
            for activity_other_id in self.activities:
                if activity_id_looking in self.activities[activity_other_id].predecessor_ids:
                    self.activities[activity_id_looking].im_looking_at.append(self.activities[activity_other_id])

    def backward_pass(self):  # 2
        is_end_task = True
        for activity in self.order_activities(self.activities, is_end_task):

            if is_end_task:
                activity.late_finish = activity.early_finish
                is_end_task = False

            elif len(activity.im_looking_at) is 0:
                activity.late_finish = self.biggest_early_finish
            else:
                lowest = 99999999
                for acti in activity.im_looking_at:
                    if acti.late_start < lowest:
                        lowest = acti.late_start
                activity.late_finish = lowest

            activity.calculate_late_start()
            activity.calculate_late_finish()
            activity.calculate_slack()
            activity.calculate_is_critical()

    @staticmethod
    def order_activities(activities, is_reverse):
        """ Returns a list of activities ordered by activiry_id
            Args:
                activities: [dictionary] dictionary in the form {activity_id, activity}
                is_reverse: [boolean] True if the activities should be in decending order. Defaults to True.
            Returns:
                Returns a list of ordered critical.Activity objects
        """
        sorted_ids = []
        for activity_id in activities:
            sorted_ids.append(activity_id)
        if is_reverse is True:
            sorted_ids.sort(reverse=is_reverse)
        else:
            sorted(sorted_ids, key=int, reverse=is_reverse)

        ordered_activities = []
        for activity_id in sorted_ids:
            if activity_id in activities.keys():
                ordered_activities.append(activities[activity_id])
        return ordered_activities

    def add_activity(self, activity_to_add):
        if activity_to_add not in self.activities:
            self.activities[activity_to_add.id] = activity_to_add
            activity_to_add.set_predecessors(self.activities)
            self.forward_pass()
            self.looking_at()
            self.backward_pass()
        else:
            pass

    def delete_activity(self, activity_to_delete):

        if activity_to_delete not in self.activities:
            del self.activities[activity_to_delete.id]
            self.forward_pass()
            self.backward_pass()
        else:
            pass

    def validate_project(self):

        circles_list = []
        for activity in self.activities:
            if activity in self.activities[activity].predecessor_ids:
                circles_list.append(activity)
        if len(circles_list) is 0:
            print("The Project is validate, there is no circle's \n")
        else:
            print("The Project NOT validate, there is circle's in: \n")
            for activity in circles_list:
                print(self.activities[activity].name + " \n")

    def find_isolated_vertices(self):
        """ returns a list of isolated vertices. """
        isolated = []
        not_isolated = True
        if len(self.activities) is 1:
            print("There is no isolated Activities")
            return

        for activity_id in self.activities:
            for activity_id_2 in self.activities:
                if activity_id in self.activities[activity_id_2].predecessor_ids or len(
                        self.activities[activity_id].predecessor_ids) is not 0:
                    not_isolated = False
            if not_isolated is True:
                isolated.append(self.activities[activity_id])
            not_isolated = True
        return isolated

    def find_critical_path_list(self):
        critical_list = []
        id_critical_list = []

        for activity_id in self.activities:
            if self.activities[activity_id].is_critical:
                id_critical_list.append(activity_id)

        for activity_id in id_critical_list:
            for activity_id_2 in id_critical_list:
                if self.activities[activity_id].early_finish <= self.activities[activity_id_2].early_finish:
                    if self.activities[activity_id_2] not in critical_list:
                        critical_list.append(self.activities[activity_id_2])
        return critical_list

    @staticmethod
    def edges(critical_list):
        edges_list = []

        for i in range(len(critical_list) - 1):
            edges_list.append((critical_list[i].name, critical_list[i + 1].name,))
        print(edges_list)
        return edges_list

    def slack_time_all_activities(self):
        slacks = []
        for activity_id in self.activities:
            if self.activities[activity_id].is_critical is False:
                slacks.append(self.activities[activity_id].slack)
        slacks.sort(reverse=True)
        return slacks


class Test(unittest.TestCase):
    p = Project()
    a = Activity(1000, 'a', 5, [])
    b = Activity(1001, 'b', 4, [])
    c = Activity(1002, 'c', 3, [1000])
    d = Activity(1003, 'd', 4, [1000])
    e = Activity(1004, 'e', 6, [1000])
    f = Activity(1005, 'f', 4, [1001, 1002])
    g = Activity(1006, 'g', 5, [1003])
    h = Activity(1007, 'h', 6, [1003, 1004])
    i = Activity(1008, 'i', 6, [1005])
    j = Activity(1009, 'j', 4, [1006, 1007])

    def test_add_all_activities(self):
        self.p.add_activity(self.a)
        self.p.add_activity(self.b)
        self.p.add_activity(self.c)
        self.p.add_activity(self.d)
        self.p.add_activity(self.e)
        self.p.add_activity(self.f)
        self.p.add_activity(self.g)
        self.p.add_activity(self.h)
        self.p.add_activity(self.i)
        self.p.add_activity(self.j)
        print(self.p.__str__() + "-----------------------------------------\n")

    def test_delete_activity(self):
        self.p.delete_activity(self.d)
        print("The Project after delete an Activity: \n")
        print(self.p.__str__() + "-----------------------------------------\n")

    # add b back.
    # p.add_activity(d)

    def test_validate(self):
        print("Check if the Project validate:")
        self.p.validate_project()
        print("-----------------------------------------\n")

    def test_find_isolated(self):
        print("Check if there is in the Project isolated Activities:")
        list_isolated = self.p.find_isolated_vertices()
        if len(list_isolated) > 1:
            print(list_isolated)
        else:
            print("\nthere is no isolated in the Project")
        print("-----------------------------------------\n")

    def test_show_critical_path_edegs(self):
        list_critical_path = self.p.find_critical_path_list()
        list_edegs = self.p.edges(list_critical_path)
        print("The critical path Activities:")
        for activiry in list_critical_path:
            print(activiry.name)
        print("The critical path Activities edges:")
        print(list_edegs)
        print("-----------------------------------------\n")

    def test_show_slack_descending(self):
        print("Slack descending order:")
        list_slack = self.p.slack_time_all_activities()
        print(list_slack)
        print("-----------------------------------------\n")

    def test_duration(self):
        print("The Duration of the Project is:")
        print(self.p.biggest_early_finish)
        print("-----------------------------------------\n")


if __name__ == "__main__":
    unittest.main()
