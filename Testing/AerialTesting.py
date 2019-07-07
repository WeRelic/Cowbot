            #return SimpleControllerState()
            if self.state != "Reset":
                self.timer = self.game_info.game_time - self.start_time

            if self.state == "Reset":
                #Reset everything
                self.timer = 0
                self.start_time = self.game_info.game_time

                #Set the game state
                ball_pos = Vec3(2000, -10, 1000)
                ball_state = self.zero_ball_state.copy_state(pos = ball_pos,
                                                             rot = Orientation(pyr = [0,0,0]),
                                                             vel = Vec3(-700, -1000, 800),
                                                             omega = Vec3(0,0,0))

                car_pos = Vec3(-600, -5300, 15)
                car_state = self.zero_car_state.copy_state(pos = car_pos,
                                                           vel = Vec3(0, 0, 0),
                                                           rot = Orientation(pitch = 0,
                                                                             yaw = pi/3,
                                                                             roll = 0),
                                                           boost = 100)

                self.set_game_state(set_state(self.game_info,
                                              current_state = car_state,
                                              ball_state = ball_state))
                self.state = "Wait"
                return SimpleControllerState()

            elif self.state == "Wait":
                if self.timer > 0.2:
                    self.state = "Plan"
                return SimpleControllerState()


            elif self.state == "Plan":
                try:
                    self.target_time, self.target_loc = get_ball_arrival(self.game_info,
                                                                         is_ball_in_scorable_box)
                except TypeError:
                    return SimpleControllerState()
                self.takeoff_time = choose_stationary_takeoff_time(self.game_info,
                                                              self.target_loc,
                                                              self.target_time)

                self.state = "Patience"
                return SimpleControllerState()


            elif self.state == "Patience":
                if self.game_info.game_time > self.takeoff_time:
                    self.state = "Initialize"

                return SimpleControllerState()


            elif self.state == "Initialize":
                self.persistent.aerial.check = True
                self.persistent.aerial.action.target = Vec3_to_vec3(self.target_loc, self.game_info.team_sign)
                self.persistent.aerial.action.arrival_time = self.target_time

                self.state = "Go"
                

                return SimpleControllerState()

            elif self.state == "Go":
                #Controller inputs and persistent mechanics
                controller_input, self.persistent = aerial(vec3_to_Vec3(self.persistent.aerial.action.target, self.game_info.team_sign),
                                                           Vec3(0,0,1),
                                                           self.game_info.dt,
                                                           self.game_info.team_sign,
                                                           self.persistent)
                if self.timer > 5:
                    self.state = "Reset"
