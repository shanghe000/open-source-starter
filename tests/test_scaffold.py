import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('new_project', Path(__file__).resolve().parents[1] / 'scripts/new_project.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ScaffoldTest(unittest.TestCase):
    def test_generated_project_has_its_own_identity_and_working_guide_links(self):
        readme = module.project_readme('my-tool', 'A useful tool', 'example-user')
        self.assertTrue(readme.startswith('# my-tool\n\nA useful tool'))
        self.assertIn('https://github.com/example-user/my-tool/actions/', readme)
        self.assertNotIn('# Open Source Starter', readme)
        for target in ['docs/ROADMAP.md', 'docs/MAINTAINER_GUIDE.md', 'CODE_OF_CONDUCT.md']:
            self.assertIn(target, readme)
            self.assertTrue((Path(__file__).resolve().parents[1] / target).is_file())


if __name__ == '__main__':
    unittest.main()
