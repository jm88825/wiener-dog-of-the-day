import { ScrollView, StyleSheet, Text } from 'react-native';
import DogCard from '../components/DogCard';
import { formatDate } from '../format';
import { colors } from '../theme';
import type { DogPick } from '../types';

export default function DayScreen({ pick }: { pick: DogPick }) {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Text style={styles.kicker}>{formatDate(pick.date)}</Text>
      <DogCard pick={pick} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 10, paddingBottom: 32 },
  kicker: {
    textAlign: 'center', color: colors.muted, fontWeight: '700', letterSpacing: 0.5,
    marginBottom: 10, textTransform: 'uppercase', fontSize: 12.5,
  },
});
