# Issue
Unable to process medium or higher quality video using `manimgl`

* Grammar : `expression-grammar.txt`
* String : `id + id / id - ( id + id )`

## Error Log

```
----------------------------------------------------------------
Common nodes = {'2', '8', '11', '3', '9', '1', '12', '7', '0', '5', '6', '4', '10'}
Common edges = {'(12,3)', '(12,11)', '(10,9)', '(2,1)', '(11,8)', '(7,6)', '(6,5)', '(3,2)', '(1,0)', '(11,7)', '(11,10)', '(12,4)'}
Transforming from [-1.79930796  0.          0.        ] to [-2.22102076  0.          0.        ]
Transforming from [ 1.03460208 -2.92387543  0.        ] to [ 0.61288927 -2.92387543  0.        ]
Transforming from [0.0899654  1.46193772 0.        ] to [-0.3317474   1.46193772  0.        ]
Transforming from [-1.73183391  1.46193772  0.        ] to [-2.15354671  1.46193772  0.        ]
Transforming from [ 1.97923875 -2.92387543  0.        ] to [ 1.55752595 -2.92387543  0.        ]
Transforming from [-1.91176471 -1.46193772  0.        ] to [-2.33347751 -1.46193772  0.        ]
Transforming from [-0.80968858  2.92387543  0.        ] to [-1.23140138  2.92387543  0.        ]
Transforming from [0.0899654 0.        0.       ] to [-0.3317474  0.         0.       ]
Transforming from [-1.97923875 -2.92387543  0.        ] to [-2.40095156 -2.92387543  0.        ]
Transforming from [ 0.0899654  -2.92387543  0.        ] to [-0.3317474  -2.92387543  0.        ]
Transforming from [ 0.0899654  -1.46193772  0.        ] to [-0.3317474  -1.46193772  0.        ]
Transforming from [-0.94463668 -2.92387543  0.        ] to [-1.36634948 -2.92387543  0.        ]
Transforming from [1.88927336 0.         0.        ] to [1.46756055 0.         0.        ]
Old nodes = set()
Old edges = set()
New nodes = {'13'}
New edges = set()
Fading in [ 2.50216263 -2.92387543  0.        ]
Traceback (most recent call last):                                                   
  File "/home/ashutosh/ManimStuff/manim/manimlib/camera/camera.py", line 346, in get_render_group_list
    return self.static_mobject_to_render_group_list[id(mobject)]
KeyError: 139697572802032

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "vis.py", line 252, in <module>
    vis.construct()
  File "vis.py", line 114, in construct
    self.play(*all_anims)
  File "/home/ashutosh/ManimStuff/manim/manimlib/scene/scene.py", line 390, in wrapper
    func(self, *args, **kwargs)
  File "/home/ashutosh/ManimStuff/manim/manimlib/scene/scene.py", line 454, in play
    self.progress_through_animations(animations)
  File "/home/ashutosh/ManimStuff/manim/manimlib/scene/scene.py", line 431, in progress_through_animations
    self.update_frame(dt)
  File "/home/ashutosh/ManimStuff/manim/manimlib/scene/scene.py", line 155, in update_frame
    self.camera.capture(*self.mobjects)
  File "/home/ashutosh/ManimStuff/manim/manimlib/camera/camera.py", line 326, in capture
    for render_group in self.get_render_group_list(mobject):
  File "/home/ashutosh/ManimStuff/manim/manimlib/camera/camera.py", line 348, in get_render_group_list
    return map(self.get_render_group, mobject.get_shader_wrapper_list())
  File "/home/ashutosh/ManimStuff/manim/manimlib/mobject/types/vectorized_mobject.py", line 901, in get_shader_wrapper_list
    fill_shader_wrappers.append(submob.get_fill_shader_wrapper())
  File "/home/ashutosh/ManimStuff/manim/manimlib/mobject/types/vectorized_mobject.py", line 883, in get_fill_shader_wrapper
    self.fill_shader_wrapper.vert_indices = self.get_fill_shader_vert_indices()
  File "/home/ashutosh/ManimStuff/manim/manimlib/mobject/types/vectorized_mobject.py", line 965, in get_fill_shader_vert_indices
    return self.get_triangulation()
  File "/home/ashutosh/ManimStuff/manim/manimlib/mobject/types/vectorized_mobject.py", line 819, in get_triangulation
    earclip_triangulation(inner_verts, rings)
  File "/home/ashutosh/ManimStuff/manim/manimlib/utils/space_ops.py", line 404, in earclip_triangulation
    new_ring = next(filter(
StopIteration
```

## Observations
1. `139697572802032` is id of the `status_mobject` which gets deleted mysteriously by the manim
2. This can be because the [`add` function calls `remove`](https://github.com/3b1b/manim/blob/9d1c8df095b47b14e5e3143655feb9a52671333e/manimlib/scene/scene.py#L204) for some reason ? Apparently this is done to prevent a single object from a group being deleted but it still doesn't explain why an `Mobject` that is live in one loop iteration is not live for another. Python versions ? Maybe. But then why would the [low resolution animation](progress_samples/ComplexEqn.mp4) render at all ?
3. This is probably related to use of `/` sign. I think it errors out on this. I might need to check this later
